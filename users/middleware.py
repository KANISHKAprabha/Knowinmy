
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import render

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract the slug from the URL
        path_parts = request.path.strip('/').split('/')

        if len(path_parts) > 0 and path_parts[0]:
            slug = path_parts[0]
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
                    print("tenant", tenant, "slug",tenant.slug)
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
                    print("222222222222222222222")
            else:
                print("user authenticate agala")
                request.tenant = None

        # Proceed if no redirection is needed
        response = self.get_response(request)
        return response












class ExceptionHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)  # Corrected to pass the request
            # Check if the response status indicates an error
            if 400 <= response.status_code < 600:
                return self.handle_http_error(request, response)  # Corrected the method call
        except IntegrityError as e:
            return self.handle_integrity_error(request, e)
        except ObjectDoesNotExist as e:
            return self.handle_object_does_not_exist(request, e)
        except Exception as e:
            return self.handle_unexpected_error(request, e)  # Separate method for unexpected errors
        
        return response 

    def handle_http_error(self, request, response):
        # Return a rendered error page with HTTP status
        return render(request, 'users/error.html', {
            'error_message': 'There is a problem with the request!',
            'error_detail': f'Status Code: {response.status_code}'
        }, status=response.status_code)  # Preserve the original status code

    def handle_integrity_error(self, request, exception):
        return render(request, 'users/error.html', {
            'error_message': 'Integrity error occurred.',
            'error_detail': str(exception)
        }, status=400)  # You may set a custom status code

    def handle_object_does_not_exist(self, request, exception):
        return render(request, 'users/error.html', {
            'error_message': 'Requested object does not exist.',
            'error_detail': str(exception)
        }, status=404)  # You may set a custom status code

    def handle_unexpected_error(self, request, exception):
        return render(request, 'users/error.html', {
            'error_message': 'An unexpected error occurred. Please try again later.',
            'error_detail': str(exception)
        }, status=500)  # You may set a custom status code

     



             
         
         
        
             
    

