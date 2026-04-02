---
name: django-codebase-audit
description: >
  Audit an existing Django project for architectural flaws, security vulnerabilities,
  data leakage, broken views, form misuse, and error-handling gaps. Trigger whenever
  a user shares Django code, asks to review a Django project, mentions issues with
  multi-tenancy, permissions, Celery tasks, payment flows, or asks "what's wrong
  with my codebase." Always use this skill even for partial code reviews.
---
 
# Django Codebase Audit Skill
 
Audit a Django project across 11 dimensions. For each area: confirm what exists,
list pros, then surface every issue with file+line evidence.
 
---
 
## Audit Dimensions & Checklist
 
### 1. Multi-Tenancy
- [ ] Tenant resolved once (middleware) and reused — not re-fetched per view
- [ ] All querysets scoped with `tenant=` filter
- [ ] `full_url` / callback URLs built with `request.build_absolute_uri()`, not hardcoded
- [ ] `Tenant.DoesNotExist` raises 404 — not silently renders homepage
- [ ] Tenant caching (cache.get_or_set) to avoid DB hit every request
 
**Known bug pattern:** Views independently calling `Tenant.objects.get(slug=slug)` despite middleware already setting `request.tenant` — middleware becomes pointless.
 
---
 
### 2. App Structure
- [ ] No wildcard imports (`from .models import *`)
- [ ] views.py < 400 lines; split by domain (billing, auth, content)
- [ ] URL namespacing: `include("app.urls", namespace="app")`
- [ ] Billing/payment code isolated from domain views
 
---
 
### 3. Authentication & Sessions
- [ ] Login failure shows error message (not blank form)
- [ ] `LOGIN_URL` defined exactly once, with leading slash
- [ ] `LOGIN_REDIRECT_URL` uses relative path or env var — not `localhost`
- [ ] `SESSION_SAVE_EVERY_REQUEST = False` (unless required)
- [ ] `create_user(username=email)` — email length ≤ 150 chars
 
---
 
### 4. Role-Based Access Control
- [ ] `check_trainer` does NOT fall through to `check_client`
- [ ] `check_student` does NOT fall through to `check_client`
- [ ] All CBVs use `check_trainer` / shared permission helper (not inline group query) — ensures superuser bypass is consistent
- [ ] Every view verifies `request.user` belongs to `request.tenant` (object-level permission)
 
**Critical pattern:** `check_trainer` including `or check_client(user)` means Clients silently pass trainer-only views.
 
---
 
### 5. Celery Tasks
- [ ] Single `Celery()` instance — not re-instantiated in `tasks.py`
- [ ] `now` called as `timezone.now()` — not compared as a function object
- [ ] No hardcoded email addresses — use `settings.ADMIN_EMAIL`
- [ ] ForeignKey fields not passed to `filter(username=fk_field)` — use `.pk` or `.email`
- [ ] Excel reads use `skiprows=` to avoid reading same rows twice
- [ ] `print()` replaced with `logger.info/error()`
 
---
 
### 6. Payment Flow
- [ ] Callback URL uses `request.build_absolute_uri()` — never `127.0.0.1:8000`
- [ ] PDF/email generation offloaded to Celery — not inside HTTP callback view
- [ ] Idempotency guard: check `order.status == ACCEPTED` before processing duplicate callbacks
- [ ] Soft-delete expired orders (`is_active=False`) — never `orders.delete()`
- [ ] `Order` created with nullable `payment_id` / `signature_id` until callback confirms
 
---
 
### 7. Data Models
- [ ] Field name matches stored unit (`duration_in_days` not `duration_in_months` storing days)
- [ ] All `created_at`/`updated_at` use `auto_now_add=True` / `auto_now=True`
- [ ] Model names spelled correctly (propagates to table name + migrations)
- [ ] `verbose_name` matches actual FK relationship
- [ ] `upload_to` on FileField is not empty string
- [ ] Denormalized counters incremented in ALL code paths that create the related object
 
---
 
### 8. Admin
- [ ] `apps.get_models()` loop excludes third-party apps (filter by `app_label`)
- [ ] Dashboard stats filtered by tenant
- [ ] Maximum two admin UIs; `ExceptionHandlingMiddleware` enabled
 
---
 
### 9. Settings & Security
- [ ] `ALLOWED_HOSTS` not `['*']` in production
- [ ] `SECRET_KEY = os.getenv('SECRET_KEY')` guarded: raise if None
- [ ] `STATIC_ROOT` resolves to a real path, not filesystem root `/`
- [ ] `LOGIN_URL` / `LOGIN_REDIRECT_URL` defined once each
- [ ] `DEFAULT_FROM_EMAIL` explicitly set
- [ ] `ExceptionHandlingMiddleware` not commented out
 
---
 
### 10. URL Routing
- [ ] All `path()` converters have closing `>` (e.g. `<slug:slug>` not `<slug:slug/`)
- [ ] No duplicate `name=` values across url patterns
- [ ] No view registered under two different URL names
- [ ] URL namespace set: `app_name = "users"` in `urls.py`
- [ ] Views that accept `<slug:slug>` in URL actually use it in function signature
 
---
 
### 11. Forms & Input Validation
- [ ] Forms that assign `instance.tenant` only do so when model has a `tenant` field
- [ ] `SubscriptionForm` (or equivalent) does NOT manually compute `id = last.id + 1` — race condition
- [ ] `OrganisationForm.save()` always overrides `client_name` with `request.user` — form passes `user=request.user`
- [ ] `ast.literal_eval` on POST data replaced with `json.loads()`
- [ ] File paths constructed from user-derived data sanitized (no `../` path traversal)
- [ ] `get()` query params validated as int before ORM use: `int(request.GET['id'])`
- [ ] Password validated through `AUTH_PASSWORD_VALIDATORS` — not raw `create_user(password=raw)`
- [ ] No `print()` in form `__init__`
 
---
 
### 12. Error Handling & Data Leakage
**Every `except Exception` block must:**
```python
except Exception as e:
    logger.exception("view_name failed: %s", e)   # ← required
    return render(request, "users/error.html", status=500)
```
 
**Leakage checklist:**
- [ ] `client_list` / any list view filters by tenant — no `Model.objects.all()`
- [ ] `enable_or_disable_user` has `@login_required` + ownership check
- [ ] `delete_trainer` has `@user_passes_test(check_client)`
- [ ] `delete_student` uses `obj = get_object_or_404(...); obj.delete()` — not chained `.delete()` then accesses `.field`
- [ ] `edit_trainer` / `edit_user` validates target `user_id` belongs to `request.tenant`
- [ ] `client_dashboard` has `@user_passes_test(check_client)`
- [ ] `home` view queries `User.objects.get(email=request.user.email)` — not `email=request.user`
 
**Broken-view pattern to detect:**
```python
# WRONG — .delete() returns (count, dict), not the object
obj = Model.objects.get(id=pk).delete()
print(obj.field)  # AttributeError every time
```
 
**Exception handler variable safety:**
```python
# WRONG — get_tenant may be undefined when exception fires
except Exception:
    return render(request, "home.html", {"get_tenant": get_tenant})  # NameError
 
# RIGHT
get_tenant = False
try:
    ...
    get_tenant = True
except Exception:
    pass
return render(request, "home.html", {"get_tenant": get_tenant})
```
 
---
 
## Severity Classification
 
| Severity | Definition |
|---|---|
| **CRITICAL** | Data exposed cross-tenant, unauthenticated mutation, view crashes on every call |
| **HIGH** | Silent error swallowing, broken logic, form→model field mismatch |
| **MEDIUM** | Race condition, path traversal risk, missing input type validation |
| **LOW** | Debug prints, inconsistent templates, naming typos |
 
---
 
## Output Format
 
For each finding output:
 
```
[SEVERITY] Area > Issue title
File: path/file.py:line
Problem: one-sentence description
Fix: one-sentence or code snippet
```
 
End with a summary table:
```
| Area | Status | Critical Issues |
|---|---|---|
```