# Knowinmy — Architecture Audit

---

## 1. Plain English Description

Knowinmy is a **multi-tenant SaaS web application** built with Django. It serves yoga and fitness organisations. Each organisation (called a **Tenant**) gets its own branded URL space — for example, `/acme-yoga/dashboard/`. Tenants subscribe to a pricing plan, onboard their trainers and students, build yoga sequences (Asanas), package them into courses, and assign students to those courses.

The system has five distinct types of users:

| Role | What they do |
|------|-------------|
| **Knowinmy staff** | Platform admins; approve subscriptions, manage all tenants |
| **Client (org admin)** | Owns the tenant; pays for subscriptions, uploads user lists |
| **Trainer** | Creates Asanas and Courses; manages assigned students |
| **Student** | Views assigned courses and postures |
| **Superuser** | Full Django admin access |

The web layer is Django. Background work (bulk emails, Excel imports, PDF invoices) runs on **Celery** workers backed by **Redis**. Payments go through **Razorpay**. In development the database is SQLite; in production it is PostgreSQL running in Docker. Error tracking uses **Sentry**.

---

## 2. Components and How They Talk to Each Other

### 2.1 Request Layer

```
Browser / Client
      │
      ▼
  Nginx (production reverse proxy)
      │
      ▼
  Gunicorn / Django runserver (port 8000)
      │
      ▼
  Django Middleware Stack
  ┌──────────────────────────────────────────┐
  │ 1. SecurityMiddleware                    │
  │ 2. SessionMiddleware                     │
  │ 3. TenantMiddleware  ◄── custom          │
  │ 4. CsrfViewMiddleware                    │
  │ 5. AuthenticationMiddleware              │
  │ 6. MessageMiddleware                     │
  │ 7. SocialAuthExceptionMiddleware         │
  └──────────────────────────────────────────┘
      │
      ▼
  URL Router (yoga/urls.py → users/urls.py)
      │
      ▼
  View function / class-based view
```

**TenantMiddleware** is the multi-tenancy linchpin. On every request it reads the first path segment (the slug), looks up the matching `Tenant` row, and attaches it to `request.tenant`. All views then filter their database queries with `tenant=request.tenant`, keeping each organisation's data completely separate. If no slug is found it renders the public homepage.

### 2.2 URL Routing

There are two URL namespaces under `yoga/urls.py`:

| Prefix | Purpose |
|--------|---------|
| `/admin/` | Standard Django admin (all models auto-registered) |
| `/custom_admin/` | Custom admin site with dashboard stats |
| `/grappelli/` | Grappelli enhanced admin UI |
| `/social-auth/` | Google OAuth2 flow |
| `/` (everything else) | `users.urls` — all application routes |

Application routes split into three groups:

- **Public** — `/`, `/register/`, `/login/`, `/subscription_plans/`, `/payment/`, `/razorpay/callback/`
- **Tenant-scoped** — `/<slug:slug>/dashboard/`, `/<slug:slug>/create_asana/`, `/<slug:slug>/trainers/`, etc.
- **Global staff** — `/organizations/`, `/organizations/<id>/send-email/`, etc.

### 2.3 Data Layer

All models live in `users/models.py`. The schema organises around `Tenant` as the root:

```
Tenant
  ├── Asana (yoga sequence, created by a trainer)
  │     └── Posture (individual pose; holds ML dataset file + snapshot image)
  ├── CourseDetails (trainer bundles Asanas into a named course)
  │     └── EnrollmentDetails (student is enrolled into one or more courses)
  ├── TrainerLogDetail (record of each onboarded trainer)
  │     └── StudentLogDetail (record of each student; links to mentor trainer)
  ├── TenantSubscription (which pricing plan the org is on)
  │     └── Order (Razorpay payment record; status: PENDING / ACCEPT / REJECT)
  └── SubscriptionChangeRequest (org requests plan change or withdrawal)

User (Django built-in)
  ├── Profile (1-to-1; address, phone, avatar)
  └── Groups → Trainer | Student | Client | Knowinmy

ClientOnboarding  (aggregate counts: trainers_onboarded, students_onboarded)
ErrorHandelingInUserUpload  (Celery task error log)
```

All deletes are **soft** — records are never removed from the database; instead `is_active` is set to `False`.

### 2.4 Async Layer (Celery + Redis)

```
Django view
    │  .delay() / .apply_async()
    ▼
Redis broker (port 6379)
    │
    ▼
Celery worker
    │
    ├── process_excel_file      — bulk user import from uploaded Excel
    ├── send_email_task         — Gmail SMTP sender (retries ×2)
    ├── send_welcome_mail_for_user — welcome emails with auto-passwords
    ├── send_payment_invoice_task  — generates ReportLab PDF, emails invoice
    ├── notify_users_for_renew  — daily midnight job: marks expired subscriptions inactive
    └── renew_subscription_task — schedules mid-cycle renewal reminder via apply_async(eta=…)

Celery Beat (scheduler)
    └── notify_users_for_renew runs at 00:00 every day (crontab)

Celery results → stored in Django DB (django-celery-results)
```

### 2.5 Payment Integration (Razorpay)

```
Client browser
    │  1. POST /payment/  (selects plan)
    ▼
subscription_payment view
    │  2. Creates Razorpay order via API
    │  3. Returns order_id + key to template
    ▼
Client browser
    │  4. Razorpay JS popup — user pays
    │  5. Browser POSTs payment_id + signature to /razorpay/callback/
    ▼
callback view
    │  6. Verifies HMAC signature
    │  7. Creates Order record (status=ACCEPT)
    │  8. Checks: does a Tenant already exist for this user?
    │
    ├── YES (renewal): TenantSubscription.objects.create(…)
    │       TenantSubscription.save() → syncs Tenant.is_active = True
    │       Dispatches send_payment_invoice_task
    │       Redirects → /<slug>/dashboard/
    │
    └── NO (new client): Redirects → /register-organisation/
            (Tenant + TenantSubscription created there)
    ▼
Celery worker
    │  9. Generates PDF invoice (ReportLab)
    │  10. Emails invoice to user
```

### 2.6 Admin Interfaces

| URL | What it shows |
|-----|--------------|
| `/admin/` | Every model in every app, auto-registered via `ListAdminMixin` |
| `/custom_admin/` | Dashboard with aggregate counts (courses, enrollments, trainers, students, Asanas) |
| `/grappelli/` | Grappelli-enhanced version of the standard admin |

### 2.7 PDF Generation

`yoga/process.py` exposes `html_to_pdf(template, context)`. It renders a Django template, encodes it as ISO-8859-1, and passes it to **xhtml2pdf** (pisa). The result is returned as an `HttpResponse` with `content_type=application/pdf`. Used by the `/pdf/` endpoint for payment invoices.

---

## 3. Main User Journey — Data Flow Diagrams

### Journey A: Organisation Signs Up and Subscribes

```
[New user]
      │
      │  GET /register/
      ▼
register view
      │  Creates: User account (no group yet)
      │  Sends welcome email via send_email_task.delay()
      │  Redirects → /login/
      │
      │  POST /login/  { username, password }
      ▼
user_login view
      │  Authenticates user
      │  TenantMiddleware: no slug yet → request.tenant = None
      │  Redirects → /subscription_plans/
      │
      │  GET /subscription_plans/--->like homepage 
      ▼
subscription_plans view
      │  Reads: Subscription.objects.filter(is_active=True)
      │  Renders: plan list with prices
      │
      │  POST /payment/  { subscription_id }
      ▼
subscription_payment view
      │  Calls Razorpay API → gets order_id
      │  Renders: payment form with Razorpay JS
      │
      │  [User pays in Razorpay popup]
      │
      │  POST /razorpay/callback/  { razorpay_payment_id, razorpay_signature, … }
      ▼
callback view
      │  Verifies HMAC signature
      │  Order.objects.create(status='ACCEPT', …)
      │  Checks: Tenant.objects.filter(client_name=user).first()
      │
      ├── Tenant found (renewal): TenantSubscription.objects.create(…)
      │       → Tenant.is_active = True (via TenantSubscription.save())
      │       → Redirects → /<slug>/dashboard/
      │
      └── No Tenant (new signup): Redirects → /register-organisation/
      │
      │  GET /register-organisation/
      ▼
register_organisation view (GET)
      │  Renders: OrganisationForm (org name, domain name)
      │
      │  POST /register-organisation/  { organization_name, domain_name, … }
      ▼
register_organisation view (POST)
      │  Creates: Tenant (slug derived from domain_name, is_active=False initially)
      │  Assigns user to Client group
      │  TenantSubscription.objects.create(plan=…, start_date=today, end_date=today+duration)
      │  Tenant.is_active = True  (synced via TenantSubscription.save())
      │  send_payment_invoice_task.delay(order_id)
      │
      ▼
[Celery worker]
      │  Generates PDF invoice (ReportLab)
      │  send_email_task.delay(subject, body, [user.email], attachment=pdf)
      ▼
[Org admin receives invoice email]
      │
      │  Redirect → /<slug>/dashboard/
      ▼
role_based_dashboard view
      │  Tenant.objects.filter(client_name=user).first()  ← .filter().first(), no DoesNotExist crash
      │  If no Tenant yet → Redirects → /register-organisation/
      │  Checks user.groups → Client
      │  Redirect → /<slug>/client_dashboard/
      ▼
[Org admin sees their dashboard]
```

---

### Journey B: Bulk Trainer & Student Onboarding

```
[Org admin]
      │
      │  GET /<slug>/trainer-approval/
      ▼
Trainer_approval_function view (GET)
      │  Renders: Excel upload form
      │
      │  POST /<slug>/trainer-approval/  { excel_file, trainer_count, student_count }
      ▼
Trainer_approval_function view (POST)
      │  Saves Excel to /media/uploads/<filename>
      │  process_excel_file.delay(file_path, admin_user_id, trainer_count, student_count, tenant_id)
      │  Returns: "processing" response immediately
      │
      ▼
[Celery worker — process_excel_file]
      │
      │  pandas.read_excel(file_path)
      │
      ├── Trainer rows (filter rows where roles == 'trainer')
      │     │  User.objects.bulk_create([…])
      │     │  Group('Trainer').user_set.add(…)
      │     │  TrainerLogDetail.objects.create(trainer_name=user, tenant=tenant)
      │     │  ClientOnboarding.trainers_onboarded += F(1)
      │     │  send_welcome_mail_for_user.delay(trainer_ids, tenant_id)
      │
      └── Student rows (filter rows where roles == 'student')
            │  User.objects.bulk_create([…])
            │  Group('Student').user_set.add(…)
            │  StudentLogDetail.objects.create(student_name=user, tenant=tenant)
            │  ClientOnboarding.students_onboarded += F(1)
            │  send_welcome_mail_for_user.delay(student_ids, tenant_id)
            │
      ▼
[Celery worker — send_welcome_mail_for_user]
      │  Generates random password per user
      │  User.set_password(password)
      │  send_email_task.delay(subject, body_with_password, [user.email])
      ▼
[Each trainer/student receives welcome email with login credentials]

      ErrorHandelingInUserUpload.objects.create(celery_msg=…, is_error=False/True)
```

---

### Journey C: Trainer Creates an Asana and Course

```
[Trainer]
      │
      │  GET /<slug>/create_asana/
      ▼
CreateAsanaView (GET)
      │  Renders: AsanaCreationForm + inline PostureFormSet
      │
      │  POST /<slug>/create_asana/  { name, no_of_postures, posture_set-* }
      ▼
CreateAsanaView (POST)
      │  form.save() → Asana.objects.create(name=…, tenant=request.tenant, created_by=request.user)
      │  For each posture in formset:
      │      Posture.objects.create(asana=asana, name=…, step_no=…, dataset=file, snap_shot=image)
      │
      │  GET /<slug>/trainer_dashboard/
      ▼
CourseCreationView (GET)
      │  QuerySet: Asana.objects.filter(tenant=request.tenant)
      │  Renders: CourseCreationForm (checkboxes of available Asanas)
      │
      │  POST /<slug>/trainer_dashboard/  { course_name, description, asanas_by_trainer }
      ▼
CourseCreationView (POST)
      │  CourseDetails.objects.create(course_name=…, user=request.user, tenant=request.tenant)
      │  course.asanas_by_trainer.set([asana_ids…])
      ▼
[Course is ready to be assigned to students]
```

---

### Journey D: Student Enrollment and Course Viewing

```
[Trainer]
      │
      │  GET /<slug>/student_mapping/
      ▼
StudentCourseMapView (GET)
      │  QuerySet: User.objects.filter(tenant=…, groups__name='Student')
      │  QuerySet: CourseDetails.objects.filter(tenant=…, user=request.user)
      │  Renders: StudentCourseMappingForm
      │
      │  POST /<slug>/student_mapping/  { students, courses }
      ▼
StudentCourseMapView (POST)
      │  EnrollmentDetails.objects.get_or_create(user=student, tenant=tenant)
      │  enrollment.students_added_to_courses.add(course)
      ▼
[Student is enrolled]

[Student]
      │
      │  GET /<slug>/user_view_asana/<course_id>/
      ▼
user_view_asana view
      │  Checks: EnrollmentDetails.students_added_to_courses contains course
      │  QuerySet: CourseDetails.asanas_by_trainer.all()
      │  Renders: list of Asanas in the course
      │
      │  GET /<slug>/user_view_posture/<asana_id>/
      ▼
user_view_posture view
      │  QuerySet: Posture.objects.filter(asana=asana, is_active=True)
      │  Renders: posture list with snapshots + ML dataset links
      ▼
[Student views and practises the poses]
```

---

### Journey E: Subscription Renewal (Automated)

```
[Celery Beat — every day at 00:00]
      │
      ▼
notify_users_for_renew task
      │
      │  QuerySet: TenantSubscription.objects.filter(is_active=True)
      │  For each subscription:
      │      if subscription.end_date < today:
      │          subscription.is_active = False
      │          subscription.save()          ← triggers Tenant.is_active = False
      │          send_email_task.delay(        ← sends "your subscription expired" email
      │              subject="Subscription Expired",
      │              recipients=[tenant.client_name.email]
      │          )
      ▼
[Org admin receives expiry notification]

      │  [Admin pays again → Journey A repeats]
```

---

### Journey F: Knowinmy Admin Flows

These are the internal platform-admin flows executed by users in the **Knowinmy** group (staff/superusers). They do not require a tenant slug — they operate across all organisations.

---

#### F1: View and Enable/Disable Organisations

```
[Knowinmy staff]
      │
      │  GET /organizations/
      ▼
organization_list_view  (@check_knowinmy)
      │  QuerySet: Tenant.objects.all()  (all tenants, no scoping)
      │  Renders: table of all organisations with enable/disable buttons
      │
      │  POST /organizations/  { action='enable'|'disable', tenant_id }
      ▼
organization_list_view (POST)
      │  Tenant.objects.filter(id=tenant_id).first()
      │  action == 'enable'  → tenant.is_active = True  ; tenant.save()
      │  action == 'disable' → tenant.is_active = False ; tenant.save()
      │  Redirects → /organizations/
      ▼
[Organisation is enabled or blocked on the platform]
```

---

#### F2: Inspect an Organisation's Asanas

```
[Knowinmy staff]
      │
      │  GET /organizations/<tenant_id>/asanas/
      ▼
asanas_view  (@check_knowinmy)
      │  tenant = Tenant.objects.get(id=tenant_id)
      │  asanas = Asana.objects.filter(tenant=tenant).prefetch_related('related_postures')
      │  get_trainer_count = TrainerLogDetail.objects.filter(tenant=tenant).count()
      │  get_stud_count    = StudentLogDetail.objects.filter(tenant=tenant).count()
      │  get_subs          = TenantSubscription.objects.filter(tenant=tenant).first()
      │  courses           = CourseDetails.objects.filter(tenant=tenant)
      │  Renders: asanas_list.html with posture snapshots, counts, subscription expiry
      ▼
[Staff can see everything the organisation has built]
      │
      │  POST /asanas/<asana_id>/remove/
      ▼
remove_asana_view  (@check_knowinmy)
      │  asana = Asana.objects.get(id=asana_id)
      │  GET  → renders confirm_remove_asana.html
      │  POST → asana.delete()          ← hard delete (known issue — should be soft)
      │  Redirects → /organizations/
```

---

#### F3: Send a Direct Email to an Organisation's Admin

```
[Knowinmy staff]
      │
      │  GET /organizations/<tenant_id>/send-email/
      ▼
send_email_view  (@check_knowinmy)
      │  tenant = Tenant.objects.get(id=tenant_id)
      │  get_client = tenant.client_name  (the org's owner User)
      │  Renders: send_email.html with message textarea
      │
      │  POST /organizations/<tenant_id>/send-email/  { message }
      ▼
send_email_view (POST)
      │  send_email_task.delay(
      │      subject='Query from Admin',
      │      message=request.POST['message'],
      │      recipient_list=[get_client.email]
      │  )
      │  Redirects → /organizations/
      ▼
[Celery worker delivers email to org admin's inbox]
```

---

#### F4: Custom / Dynamic Subscription Pricing Flow

This is a separate end-to-end flow that allows a user to **build their own subscription plan**, which then sits in a pending queue until Knowinmy staff review and approve it. Only after approval does the plan appear on the homepage banner for that user to proceed to payment.

```
STEP 1 — User builds a custom plan
─────────────────────────────────────────────────────────────

[Logged-in user (no org yet)]
      │
      │  GET /subscribe/
      ▼
dynamic_subscription_payment view
      │
      ├── Branch A: session holds a subscription_id AND it is approved (is_active=True)
      │       Subscription.objects.filter(id=session['subscription_id']).first()
      │       Renders SubscriptionForm pre-filled; user can pay immediately
      │
      ├── Branch B: session holds a subscription_id but plan is still pending
      │       Renders read-only form showing "awaiting admin approval"
      │
      └── Branch C: no session key yet
              Renders blank SubscriptionForm with live price calculator
              (AJAX POST: price = asanas×10 + students×50 + trainers×100 + months×200)
              │
              │  POST /subscribe/  { no_of_students, no_of_trainers,
              │                      permitted_asanas, duration_in_months }
              ▼
              dynamic_subscription_payment (POST)
                    │  Calculates price formula
                    │  Subscription.objects.create(
                    │      name=user.first_name,       ← named after user
                    │      is_active=False,            ← PENDING; not live yet
                    │      description="Dynamic subscription",
                    │      price=calculated_price,
                    │      …
                    │  )
                    │  request.session['subscription_id'] = new_sub.id
                    │  request.session['subscription_price'] = price
                    │  Redirects → / (homepage)
                    ▼
              [User lands on homepage; banner shows their pending plan]


STEP 2 — Knowinmy staff reviews and approves/edits/rejects
─────────────────────────────────────────────────────────────

[Knowinmy staff]
      │
      │  GET /review-ds/
      ▼
review_dynamic_subscription view
      │  QuerySet: Subscription.objects.filter(is_active=False)
      │            ← all pending custom plans, including the user's
      │  Renders: review_ds.html with editable fields per pending plan
      │
      │  POST /review-ds/  { subscription_id, action='edit'|'approve'|'reject', … }
      ▼
review_dynamic_subscription (POST)
      │
      ├── action == 'edit':
      │       Updates: no_of_trainers, no_of_students, duration_in_months, price,
      │                created_at, updated_at  on the Subscription row
      │       Saves with full_clean() validation
      │       (staff can adjust the price/terms before approving)
      │
      ├── action == 'approve':
      │       subscription.is_active = True   ← publishes the plan; user can now pay
      │       subscription.save()
      │       Redirects → /organizations/
      │
      └── action == 'reject':
              subscription.delete()           ← hard delete; plan removed entirely
              Redirects → /organizations/


STEP 3 — User sees approved plan on homepage banner and proceeds to pay
─────────────────────────────────────────────────────────────

[User returns to homepage /]
      │
      ▼
home / home_slug view
      │  Reads session: subscription_id = request.session.get('subscription_id')
      │  Subscription.objects.filter(id=subscription_id).first()
      │  home_page.html receives the subscription → renders it as a banner/card
      │  get_transaction = Order.objects.filter(user=current_user).exists()
      │  get_tenant     = Tenant.objects.filter(client_name=current_user).exists()
      │  (Banner only shows if the user has no completed order / no org yet)
      │
      │  User clicks the banner → GET /payment/ (session still holds subscription_id)
      ▼
subscription_payment view
      │  subscription = Subscription.objects.filter(id=session['subscription_id']).first()
      │  Calls Razorpay API with subscription.price → gets order_id
      │  Renders payment form
      │
      │  [User pays in Razorpay popup]
      │
      │  POST /razorpay/callback/
      ▼
callback view
      │  Verifies HMAC signature
      │  Order.objects.create(status='ACCEPT', subscription=custom_sub, …)
      │  Redirects → /register-organisation/
      │
      │  [User creates org → Journey A continues from Step 5 onwards]
      ▼
[Organisation is live on their custom plan]
```

#### F4b: Create a Coupon for an Organisation (stub)

```
[Knowinmy staff]
      │
      │  GET /organizations/<tenant_id>/create-coupon/
      ▼
create_coupon_view  (@check_knowinmy)
      │  Renders: create_coupon.html (discounted_price + subscription selector)
      │  POST: reads discounted_price + subscription_id
      │  [Coupon save and email dispatch are not yet implemented — stub only]
      │  Redirects → /organizations/
```

---

#### F5: Review and Approve/Reject an Org's Slug Change Request

```
[Client (org admin)]
      │
      │  GET /<slug>/request-slug-change/
      ▼
request_slug_change  (@check_client)
      │  tenant = Tenant.objects.get(client_name=request.user)
      │  Renders: SlugChangeRequestForm
      │
      │  POST /<slug>/request-slug-change/  { slug_change_requested }
      ▼
request_slug_change (POST)
      │  tenant.slug_change_requested = new_slug
      │  tenant.slug_approved = False
      │  tenant.save()
      │  send_email_task.delay(subject="Slug change requested", recipient=[admin.email])
      │  Redirects → /<slug>/get-subs/
      │
      ▼  [Knowinmy staff is notified]

[Knowinmy staff]
      │
      │  GET /review-slug-changes/
      ▼
review_slug_changes  (no role guard — open to any authenticated user; known issue)
      │  QuerySet: Tenant.objects.filter(slug_change_requested__isnull=False, slug_approved=False)
      │  Renders: table of pending slug change requests
      │
      │  POST /review-slug-changes/  { tenant_id, action='approve'|'reject' }
      ▼
review_slug_changes (POST)
      │
      ├── action == 'approve':
      │       old_slug = tenant.slug
      │       tenant.slug = tenant.slug_change_requested
      │       tenant.domain_name = new_slug
      │       tenant.slug_approved = True
      │       tenant.slug_change_requested = None
      │       tenant.save()
      │       — cascades: updates CourseDetails, EnrollmentDetails, TrainerLogDetail,
      │                   StudentLogDetail, ClientOnboarding, Asana, Posture FKs
      │       send_slug_change_notification(tenant, request)
      │
      └── action == 'reject':
              tenant.slug_change_requested = None
              tenant.save()
              send_slug_reject_notification(tenant, request)
      ▼
[Org admin receives approval/rejection email; all URLs now work under new slug]
```

---

#### F6: Review and Approve/Reject a Subscription Change Request

```
[Client (org admin)]
      │
      │  GET /<slug>/request-subscription-change/
      ▼
subscription_change_request  (@check_client)
      │  SubscriptionChangeForm → request_type ('change' or 'withdraw') + reason
      │
      │  POST → SubscriptionChangeRequest.objects.create(
      │              tenant=tenant, request_type=…, reason=…, approved=False)
      │  send_email_task.delay("subscription change requested", [admin.email])
      │  Redirects → /<slug>/trainer-approval/
      │
      ▼  [Knowinmy staff is notified]

[Knowinmy staff]
      │
      │  GET /subscription-requests/
      ▼
list_subscription_requests  (@check_knowinmy)
      │  QuerySet: SubscriptionChangeRequest.objects.filter(approved=False)
      │  Renders: table of pending requests
      │
      │  POST /approve-subscription-change/<request_id>/
      │        { action='approve'|'reject' }
      ▼
approve_subscription_change_by_knowinmy
      │  subscription_request = SubscriptionChangeRequest.objects.get(id=request_id)
      │  tenant  = Tenant linked to request
      │  get_order = Order.objects.filter(user=client, tenant=tenant).first()
      │
      ├── action='approve' + request_type='withdraw':
      │       tenant.is_active = False
      │       get_order.delete()          ← hard delete (known issue)
      │       tenant.save()
      │       send_email_task.delay("withdrawal approved", [client.email])
      │
      ├── action='reject'  + request_type='withdraw':
      │       tenant.is_active = True
      │       tenant.save()
      │       send_email_task.delay("withdrawal rejected", [client.email])
      │
      └── action='approve' + request_type='change':
              subscription_request.approved = True
              subscription_request.save()
              [org admin proceeds to /payment/ to pick a new plan → Journey A]
      ▼
[Organisation's access updated; admin receives decision email]
```

---

## 4. Component Interaction Summary

```
                        ┌─────────────────────────────────────┐
                        │           Browser / Client           │
                        └──────────────┬──────────────────────┘
                                       │ HTTP
                        ┌──────────────▼──────────────────────┐
                        │         Nginx (prod only)            │
                        └──────────────┬──────────────────────┘
                                       │
                        ┌──────────────▼──────────────────────┐
                        │        Django Application            │
                        │  ┌────────────────────────────────┐ │
                        │  │     TenantMiddleware            │ │
                        │  │  (attaches request.tenant)      │ │
                        │  └───────────────┬────────────────┘ │
                        │  ┌───────────────▼────────────────┐ │
                        │  │  URL Router → Views             │ │
                        │  │  permissions.py (role checks)   │ │
                        │  └───┬───────────┬────────────────┘ │
                        │      │           │                   │
                        │  ┌───▼───┐   ┌───▼──────────────┐  │
                        │  │  DB   │   │  Celery .delay() │  │
                        │  │SQLite │   └────────┬─────────┘  │
                        │  │  or   │            │             │
                        │  │  PG   │            │             │
                        │  └───────┘            │             │
                        └─────────────────────────────────────┘
                                               │
                        ┌──────────────────────▼──────────────┐
                        │         Redis (broker)               │
                        │         port 6379                    │
                        └──────────────────────┬──────────────┘
                                               │
                        ┌──────────────────────▼──────────────┐
                        │         Celery Worker                │
                        │  process_excel_file                  │
                        │  send_email_task (Gmail SMTP)        │
                        │  send_payment_invoice_task (PDF)     │
                        │  notify_users_for_renew (daily)      │
                        └──────────────────────┬──────────────┘
                                               │
                        ┌──────────────────────▼──────────────┐
                        │  External Services                   │
                        │  • Gmail SMTP (email)                │
                        │  • Razorpay API (payments)           │
                        │  • Google OAuth2 (login)             │
                        │  • Sentry (error tracking)           │
                        └─────────────────────────────────────┘
```

---

## 5. Known Issues (Outstanding)

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | High | `settings.py:335,362` | Sentry initialised twice — second call silently overrides first |
| 2 | High | `settings.py:260` | `CSRF_TRUSTED_ORIGINS` missing comma between entries (syntax error) |
| 3 | High | `settings.py` | `STATIC_ROOT = os.path.join(BASE_DIR, '/')` resolves to filesystem root `/` |
| 4 | High | `middleware.py` | `ExceptionHandlingMiddleware` is defined but commented out — unhandled exceptions reach users raw |
| 5 | Medium | `views.py` | 100+ `print()` statements left in production code — use `logger` instead |
| 6 | Medium | `tasks.py` | Excel parser reads both trainer and student rows from row 0 — may skip data |
| 7 | Medium | `views.py` | `client_list()` view has no `tenant=` filter — cross-tenant data leak |
| 8 | Medium | `users/urls.py` | No `app_name` namespace — URL names risk collision with other apps |
| 9 | Low | `models.py` | `Subscription.duration_in_months` stores a `timedelta(days=N)`, not months — misleading name |
| 10 | Low | `views.py` | Wildcard imports (`from .models import *`) throughout codebase |
| 11 | Low | `tests.py` | All tests commented out — zero active test coverage |

---

## 6. Resolved Issues (Fixed 2026-04-20)

| # | Location | Issue | Fix |
|---|----------|-------|-----|
| R1 | `views.py — review_dynamic_subscription` | Crashed with `ValueError: view returned None`; queried `filter(active=False)` after field was removed in migration 0002 | Added `is_active` field back to `Subscription` model + migration `0003_subscription_is_active.py`; rewrote view with correct field name and always returns a response |
| R2 | `views.py — dynamic_subscription_payment` | Form didn't autofill after admin approval; `filter(name=user)` compared string column to User object (always None); `session['subscription_id']` never set before payment redirect | Rewrote view with 3 clean branches (no submission / pending / approved+autofill); lookup now uses `session['subscription_id']`; session key set immediately on POST; removed spurious `subscription_id` hidden field from `SubscriptionForm` |
| R3 | `views.py — razorpay_callback` + `role_based_dashboard` | `Tenant matching query does not exist` at dashboard line 1027 on new signup and on renewal after expiry | Callback now branches on Tenant existence: renewal path creates new `TenantSubscription` (syncs `Tenant.is_active=True`) and redirects to dashboard; new-client path redirects to `register_organisation`. Dashboard changed `.get()` to `.filter().first()` — no `DoesNotExist` crash; new clients redirected gracefully |

---

*Generated by Claude Code — 2026-04-20 | Updated 2026-04-20*
