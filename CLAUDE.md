# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Knowinmy is a multi-tenant SaaS platform for yoga/fitness organizations. Each tenant (organization) gets its own slug-based URL space (`/<slug>/...`). Tenants onboard trainers and students, create yoga Asanas (sequences of Postures), and assign them to courses. The Django project is named `yoga`; the primary app is `users`.

## Commands

All commands run from `knowinmy_python_code_base/`.

**Development server:**
```bash
python manage.py runserver
```

**Apply migrations:**
```bash
python manage.py migrate
```

**Run tests:**
```bash
python manage.py test users
```

**Celery worker + beat (combined):**
```bash
celery -A yoga worker -B -l info --autoscale=10,1
```

**Flower (Celery monitoring UI on port 5555):**
```bash
flower --port=5555 --broker=redis://redis:6379/0
```

**Production (Docker):**
```bash
docker-compose build && docker-compose up -d
```

## Environment Variables

Copy and populate a `.env` file with:
- `SECRET_KEY` — Django secret key
- `IS_PRODUCTION` — set to `True` for production (switches DB to PostgreSQL, disables DEBUG)
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`
- `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET` — payment integration
- `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`, `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` — Google OAuth
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` — Gmail SMTP

Development uses SQLite by default (`IS_PRODUCTION` not set). Production uses PostgreSQL with host `postgres` (Docker service name).

Redis runs on port **6380** for cache and Celery broker in development.

## Architecture

### Multi-tenancy

Tenancy is implemented via the `Tenant` model (not django-tenants). Each `Tenant` has a `slug` derived from `domain_name`. The `TenantMiddleware` (`users/middleware.py`) attaches the current tenant to the request. Nearly every model has a `tenant` FK. Tenant-scoped URLs are prefixed with `/<slug:slug>/`.

### Data Model (`users/models.py`)

```
Tenant (org) → Asana → Posture (steps with ML dataset files and snapshots)
Tenant → CourseDetails (M2M to Asana, FK to trainer User)
Tenant → EnrollmentDetails (M2M to CourseDetails, FK to student User)
Tenant → TrainerLogDetail / StudentLogDetail (onboarding logs)
Tenant → ClientOnboarding (counts trainers/students onboarded)
Tenant → SubscriptionChangeRequest
Subscription → Order (Razorpay payment record)
User → Profile (extended info)
```

### User Roles

Handled via Django `Group` model: `Trainer`, `Student`, and client/admin roles. `role_based_dashboard` view routes users to the appropriate dashboard based on group membership.

### Bulk User Onboarding

Clients upload an Excel file; the view dispatches `process_excel_file` (a Celery task in `users/tasks.py`) which reads rows, creates `User` objects in bulk, assigns groups, and creates `TrainerLogDetail`/`StudentLogDetail` records. Errors are written to `ErrorHandelingInUserUpload`.

### Celery Tasks (`users/tasks.py`)

- `process_excel_file` — bulk user onboarding from Excel
- `send_email_task` — async email via Gmail SMTP
- `notify_users_for_renew` — daily subscription expiry check (scheduled at midnight)
- `renew_subscription_task` — sends mid-cycle renewal reminders using `apply_async(eta=...)`
- `send_welcome_mail_for_user` — sends welcome emails with auto-generated passwords

Beat schedule is defined both in `yoga/celery.py` and `yoga/settings.py` (`CELERY_BEAT_SCHEDULE`).

### Admin

Three admin interfaces are registered:
- `/admin/` — standard Django admin (all models auto-registered via `ListAdminMixin`)
- `/custom_admin/` — `CustomAdminSite` with dashboard stats
- `/grappelli/` — Grappelli UI

### PDF Generation

`yoga/process.py` provides `html_to_pdf(template_src, context_dict)` using xhtml2pdf. Used by the `/pdf/` endpoint.

### Payment Flow

Razorpay integration: `subscription_payment` view creates an order, the client pays, and `/razorpay/callback/` verifies the signature and creates an `Order` record.

## Key Files

| File | Purpose |
|------|---------|
| `yoga/settings.py` | All config; env-driven production/dev switching |
| `yoga/celery.py` | Celery app + beat schedule |
| `yoga/urls.py` | Root URL conf (includes `users.urls`) |
| `users/models.py` | All domain models |
| `users/tasks.py` | All Celery tasks |
| `users/admin.py` | Auto-registers all models + custom admin site |
| `yoga/process.py` | HTML→PDF utility |
| `distance_script/` | Standalone JS/HTML for pose distance calculation (not part of Django) |

## Notes

- Tests exist in `tests.py` and `users/tests/` but are all commented out — there is effectively no active test suite.
- `Subscription.duration_in_months` is saved as days (`timedelta(days=duration_in_months)`), not actual months — this is a known inconsistency in the model.
- The `Pipfile` reflects an older dependency set (Django 4.1.2); `requirements.txt` is the authoritative production dependency list (Django 4.1.13).
## Auto-Load Skills
At the start of every session, read `context_skills.md` from the project root
and use it as your working guidelines for all tasks in this project.

## Working Rules
- Fix CRITICAL issues before touching anything else
- Never delete DB records — use `is_active=False` soft delete
- Every `except Exception` block must call `logger.exception()`
- Always filter querysets with `tenant=` scope