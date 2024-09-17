# from django.shortcuts import render
# from django.contrib.sessions.models import Session
# import random
# class ExceptionHandlingMiddleware:
#     """Handle uncaught exceptions instead of raising a 500.
#     """
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         return self.get_response(request)

#     def process_exception(self, request, exception):

#         if isinstance(exception, CustomMiddlewareException):
#             # Show warning in admin using Django messages framework
#             messages.warning(request, str(exception))
#             # Or you could return json for your frontend app
#             return JsonResponse({'error': str(exception)})

#         return None  # Middlewares should return None when not applied



from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import *

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract the slug from the URL
        path_parts = request.path.strip('/').split('/')

        if len(path_parts) > 1 and path_parts[1]:
            slug = path_parts[1]
            print(slug, "line 40")

            try:
                tenant = Tenant.objects.get(slug=slug)
                request.tenant = tenant

                # Handle redirection after login based on user role (group)
                if request.path == '/login/' and tenant and request.user.is_authenticated:
                    # Check the user's group and redirect accordingly

                    if request.user.groups.filter(name='Trainer').exists():
                        # Redirect to trainer dashboard
                        return HttpResponseRedirect(reverse('view-trained', kwargs={'slug': tenant.slug}))
                    elif request.user.groups.filter(name='Student').exists():
                        # Redirect to student dashboard
                        return HttpResponseRedirect(reverse('student-mapp-courses', kwargs={'slug': tenant.slug}))
                    else:
                        # Default role or unauthorized role
                        return HttpResponseRedirect(reverse('Trainer-approval', kwargs={'slug': tenant.slug}))

            except Tenant.DoesNotExist:
                # Redirect to an error page if tenant is not found
                print("hello")

        else:
            # Handle requests without a slug (like login)
            if request.user.is_authenticated:
                try:
                    tenant = Tenant.objects.get(client_name=request.user)
                    print(tenant,"lin")
                    request.tenant = tenant
                    
                    if request.user.groups.filter(name='Trainer').exists():
                        # Redirect to trainer dashboard
                        return HttpResponseRedirect(reverse('view-trained', kwargs={'slug': tenant.slug}))
                    elif request.user.groups.filter(name='Student').exists():
                        # Redirect to student dashboard
                        return HttpResponseRedirect(reverse('student-mapp-courses', kwargs={'slug': tenant.slug}))
                    else:
                        # Default role or unauthorized role
                        return redirect(reverse('Trainer-approval', kwargs={'slug': tenant.slug}))
  

                except Tenant.DoesNotExist:
                    # return HttpResponseRedirect('tenant-not-found',kwargs={'slug': tenant.slug})
                    print("hello    ")
            else:
                request.tenant = None

        # Proceed if no redirection is needed
        response = self.get_response(request)
        return response
