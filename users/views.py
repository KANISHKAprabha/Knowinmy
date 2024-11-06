from decimal import Decimal
import json
import os
import time
import sweetify
from .tables import *
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.db.models import F
from django.contrib.auth import authenticate, update_session_auth_hash
from django.http import HttpResponseRedirect
from django.db.models import Count
from django.db.models import Sum
from django.contrib.auth.hashers import make_password
from .tasks import *
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import *
from django.contrib import messages as django_messages

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import  logout
from sentry_sdk import capture_exception
from django.views import View
# from bulkmodel.models import BulkModel
from django.contrib import messages


from django.db import transaction
from django.utils.decorators import method_decorator

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg
from django.views.decorators.csrf import csrf_exempt
from django.forms import formset_factory
from pyexpat.errors import messages
from django.contrib.auth.models import Group
from django.conf import settings
from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from .models import *
from .forms import *
from django.contrib.auth import authenticate,login
from django.contrib import auth
from django.utils import timezone
from django.contrib.auth.decorators import login_required,user_passes_test
from .permissions import *
from django.contrib.auth.models import User, Group
from import_export.formats.base_formats import XLSX
from tablib import Dataset
import ast
from django.db import IntegrityError, transaction
import razorpay
import pandas as pd
import base64
from django.shortcuts import render
from openpyxl import load_workbook
import sweetify
from django.dispatch import receiver

from .utils import  calculate_asana_overall_accuracy, calculate_user_overall_accuracy
from django.views.decorators.http import require_http_methods

import logging
logger = logging.getLogger(__name__)

def send_email(recipient_list, subject, message, from_email=settings.EMAIL_HOST_USER):
    """
    Send an email to a list of recipients.

    Args:
        recipient_list (list): List of email addresses to send the email to.
        subject (str): Subject of the email.
        message (str): Body of the email.
        from_email (str): The sender's email address. Defaults to settings.EMAIL_HOST_USER.
    """
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )


def register(request):
    
 try:
    if request.method == "POST":

        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")

        user = User.objects.create_user(username=email,email=email,first_name=first_name,last_name=last_name,password=password)
        user.save()
        send_email(
            subject="Registeration in Knowinmy",
            message="Welcome to our website to enchance your tutor skills in  AI assisted website",
            from_email="prabhaprasath07@gmail.com",
            recipient_list=[email],
            fail_silently=False,


                   )
        
      
        return redirect('login')
    return render(request , "users/user_register.html")
 except IntegrityError:
     messages.error(request,"A user with this email already exist")
 except  Exception as e:
      return render(request,'error.html')




@login_required
def   profile_view(request, slug=None):
    try:
      if slug:
        tenant = Tenant.objects.get(slug=slug)
        print(tenant)
        if request.method == 'POST':
            # address = request.POST.get("address")
            # phone_number= request.POST.get("phone_number")
            # city = request.POST.get("city")
            # state= request.POST.get("state")

            print("hello world")
            profile, created = Profile.objects.get_or_create(user=request.user)
            form = ProfileForm(request.POST, instance=profile)
            print(profile.address,profile.city,"oppppppppppppppppppppppp")

           
            print(form,"llllllllllllllll")
            if form.is_valid():
                form.save()
                print(profile,"fom after save")
                return render(request, 'users/profile.html', {
            'user': request.user,
            'tenant':tenant,
            'slug': tenant.slug,
            'form':form,
            'profile':profile
            
            })
                
               
        else:
            form = ProfileForm()  
            profile, created = Profile.objects.get_or_create(user=request.user)    
            return render(request, 'users/profile.html', {
            'user': request.user,
            'tenant':tenant,
            'slug': tenant.slug,
            'form':form,
              'profile':profile
         
            
            })
      else:
          return render(request,'users/profile.html',{
              'user': request.user,
              
          })
    except Exception as e:
        print(e,"hello")
        return render(request, 'users/error.html')


@login_required
def update_profile(request,slug):
    try:
        tenant=Tenant.objects.get(slug=slug)
        profile, created = Profile.objects.get_or_create(user=request.user)
        print(profile,"ooooooooooooooooooooooo")

        if request.method == 'POST':
            # address = request.POST.get("address")
            # phone_number= request.POST.get("phone_number")
            # city = request.POST.get("city")
            # state= request.POST.get("state")

            print("hello world")

            form = ProfileForm(request.POST, instance=profile)
           
            print(form,"llllllllllllllll")
            if form.is_valid():
                form.save()
               
                return redirect('role_based_dashboard')  # Redirect back to profile page with slug
        else:
            form = ProfileForm(instance=profile)
        
        return render(request, 'users/profile.html', {
            'user': request.user,
            'form': form,
            'profile': profile,
            'slug':tenant.slug,
            'tenant':tenant
        })
    except Exception as e:
        return render(request, 'error.html')

def send_payment_invoice(request,order):
    user=request.user
    print(user,"hello world ")
    current_user=User.objects.filter(username=user).first()
    get_email=current_user.email
    print(get_email,"hello")

    subject = f"Payment Invoice for Order {order.provider_order_id}"
    message = f"""
    Dear Customer,

    Thank you for your payment. Here are the details of your transaction:

    Order ID: {order.provider_order_id}
    Payment ID: {order.payment_id}
    Amount: {order.amount}  # Assuming there's an amount field in your Order model
    Status: {order.status}
    Date: {order.created_at}

    We appreciate your business!

    Best regards,
    Your Company Name
    """
    from_email = settings.DEFAULT_FROM_EMAIL  # Make sure to set this in your settings.py
    recipient_list = [get_email]  # Replace with the actual field containing the customer's email

    # Send the email
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )
@login_required
def subscription_payment(request):
 try:
    
    current_user=request.user
    print(current_user,"Current user")
   
   
   
   

    if request.method == "POST":
        username = request.user
        print(username,"lollllll")
        get_only_username=User.objects.get(username=current_user)
        name=get_only_username.first_name
        print(name,"line no 111")
        subscription_id = request.POST.get("subscription_id")
        print(subscription_id)
        coupon_code = request.POST.get("coupon_code")
        subscription = Subscription.objects.get(id=subscription_id)
        
        amount = Decimal(subscription.price)
        discounted_amount_after_negotiation = amount

        if coupon_code:
            print(coupon_code,"kaniiis")
            try:
                coupon = CouponCodeForNegeotiation.objects.get(code=coupon_code)
                
                
                amount = coupon.discounted_price
                print(amount)
            except CouponCodeForNegeotiation.DoesNotExist as e:
                print("No coupon found")
                capture_exception(e)
                # Proceed with the original amount if the coupon code is invalid

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create(
            {"amount": int(amount * 100), "currency": "INR", "payment_capture": "1"}
        )
        order = Order.objects.create(
          
            subscription=subscription,
            name=name,
            amount=amount,
            provider_order_id=razorpay_order["id"]
        )
        order.save()
        group, _ = Group.objects.get_or_create(name='Client')
        if not current_user.groups.filter(name='Client').exists():
            current_user.groups.add(group)
            current_user.save() 
        send_payment_invoice(request,order)   

        return render(
            request,
            "users/callback.html",
            {
                "callback_url": "http://" + "127.0.0.1:8000" + "/razorpay/callback/",
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,
            },
        )
    else:
        print("entered elseeeeeeeeee")
        username = request.user
        print(username,"lollllll")
        get_only_username=User.objects.get(username=username)
        name=get_only_username.first_name
        print(name,"line no 111")
        subscription_id = request.session.get('subscription_id')
        print(subscription_id,"llllllllll")
        subscription = Subscription.objects.get(id=subscription_id)
        amount = Decimal(subscription.price)
       
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create(
            {"amount": int(amount * 100), "currency": "INR", "payment_capture": "1"}
        )
        order = Order.objects.create(
          
            subscription=subscription,
            name=name,
            amount=amount,
            provider_order_id=razorpay_order["id"],
            
        )
        order.save()
         # send_payment_invoice(order,request)
            # group, _ = Group.objects.get_or_create(name='Client')
            # current_user.groups.add(group)
        print("order saved")
        group, _ = Group.objects.get_or_create(name='Client')
        if not current_user.groups.filter(name='Client').exists():
            current_user.groups.add(group)
            current_user.save() 
        send_payment_invoice(request,order)    
        
 
                   

        return render(
            request,
            "users/callback.html",
            {
                "callback_url": "http://" + "127.0.0.1:8000" + "/razorpay/callback/",
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,
               
            },
        )   
        
        

    
 except Exception as e:
      print(e,"ppppppppppppppp")
      return render(request,'users/error.html')



@csrf_exempt
def callback(request):
    # tenant = request.tenant  # Assuming the tenant is set in the middleware
  try:
   

    def verify_signature(response_data):
        
        time.sleep(2)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            return client.utility.verify_payment_signature(response_data)
        except razorpay.errors.SignatureVerificationError:
            return False

    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.created_at=timezone.now()
        order.is_active=True
        order.updated_at=timezone.now()
        # order.tenant=request.tenant
        order.save()
        
        if verify_signature(request.POST):
            order.status = 'ACCEPT'
            order.save()
            context={
                'order':order,
                # 'idempo_token': idempo.token,
            }
           
          
 
           
            
            print("SUCCESS")
            return render(request, "users/success.html",context)
        else:
            order.status = 'REJECT'
            order.save()
            print("FAILURE: Signature verification failed.")
            return render(request, "users/success.html", context={'order':order})
    else:
        try:
            payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
            provider_order_id = json.loads(request.POST.get("error[metadata]")).get("order_id")
        except (TypeError, json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing error metadata: {e}")
            capture_exception(e)
            return render(request, "users/callback.html", context={"status": 'REJECT'})

        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.status = 'REJECT'
        order.save()
        print("FAILURE: Error in payment process.")
        return render(request, "users/callback.html", context={"status": order.status})
  except Exception as e:
       print(e,"hello error")
       return render(request,'users/error.html')

# integrity error need to handle in this view - username must be unique


@login_required
@user_passes_test(check_client)
def Trainer_approval_function(request,slug):
    try:
        # Get the tenant from the request
        tenant = getattr(request, 'tenant', None) or  Tenant.objects.get(slug=slug)     
        print(tenant,"line ")

        if tenant is None:
            return render(request, 'error.html', {'message': 'Tenant not found'})

        if request.method == 'POST':
            admin_user = request.user
            get_name=User.objects.filter(username=admin_user).first()
            get_name_email=get_name.email
            print(admin_user,"line 209")

          
            order_transaction = Order.objects.filter(
                name=get_name.first_name,
                status='ACCEPT',
                 # Filter based on tenant
            ).first()
            print(tenant,admin_user,"line 288")
            print(order_transaction,"line 217")

            if not order_transaction:
                print("line no 232ijdsij")
                sweetify.warning(request, "No transaction found", button="OK")
                return render(request, 'users/Trainer_approval_Page.html')

            subscription = order_transaction.subscription
            no_of_persons_onboard_by_client = subscription.no_of_persons_onboard
            no_of_persons_needed_to_onboard=ClientOnboarding.objects.filter(client=request.user,tenant=tenant).first()
            x=no_of_persons_needed_to_onboard.trainers_onboarded
            y=no_of_persons_needed_to_onboard.students_onboarded
            tot=no_of_persons_onboard_by_client-(x+y)
            print(tot,"line no 225")

            # Handle file upload
            uploaded_file = request.FILES.get('excel_file')
            if uploaded_file:
                admin_user_id = admin_user.id
                print(admin_user_id,"line 231")

                # Save the uploaded file temporarily
                file_path = default_storage.save(f'temp/{uploaded_file.name}', ContentFile(uploaded_file.read()))
                
                # Pass file path, admin user ID, and tenant information to the Celery task
                process_excel_file.delay(file_path, admin_user_id, tot, tenant.id)
                send_email(
            subject="Onboarding users in Knowinmy",
            message="You have onboarded the users successfully ",
            from_email="prabhaprasath07@gmail.com",
            recipient_list=[get_name_email],
            fail_silently=False,


                   )
                

                django_messages.success(request, "Users are being onboarded, you'll be notified once done.", button="OK")
            else:
                django_messages.error(request, "No file uploaded!", button="OK")

            return render(request, 'users/Trainer_approval_Page.html',{'tenant': tenant,"slug":tenant.slug})

        else:
            return render(request, 'users/Trainer_approval_Page.html',{'tenant': tenant,"slug":tenant.slug})

    except Exception as e:
        print(e)
        capture_exception(e)
        django_messages.error(request, "Error from our side ")
        return render(request,'users/error.html')
    


@login_required
@user_passes_test(check_superuser)   
def client_list(request):
    table=ClientTable(Order.objects.all())

    print(table,"print this tosd")
    return render(request,'users/client_table.html',{'table':table})



@login_required
def onboarding_view(request,slug):
  try:
    admin_user = request.user
    user_email=User.objects.get(username=admin_user)
    print(user_email,"pppppppppjij")
    username_client=user_email.first_name
    print(username_client,"oooooooooooo")
    print(admin_user,"line no 281")
    tenant_name = Tenant.objects.get(slug=slug)
    
    tenant= tenant_name
    print(tenant,"line 276")
    # Assuming tenant is set in middleware

    # Filter the order by tenant and user
    order_transaction = Order.objects.filter(name=username_client, status='ACCEPT').first()
    print(order_transaction,"llllllllllllllllllllllllllllllllll")

    print(tenant,admin_user,"line no 292")
    print(order_transaction,"likkk")

    if not order_transaction:
        tenant = Tenant.objects.get(slug=slug)
        sweetify.warning(request, "No transaction found", button="OK")
        django_messages.error(request,"No transaction found")
        print("No transaction found")
        print("hello")
        return render(request,'users/Trainer_approval_Page.html', {'slug':tenant.slug,'tenant':tenant})
    subscription = order_transaction.subscription
    print(subscription, "Subscription Details")
    no_of_persons_onboard_by_client = subscription.no_of_persons_onboard
    print(no_of_persons_onboard_by_client)
    
    no_of_persons_needed_to_onboard=ClientOnboarding.objects.filter(client=request.user,tenant=tenant).first()
    x=no_of_persons_needed_to_onboard.trainers_onboarded
    y=no_of_persons_needed_to_onboard.students_onboarded
    total=no_of_persons_onboard_by_client-(x+y)
    print(total,"line no 225")
    print(no_of_persons_onboard_by_client, "Max Persons to Onboard")

    # Check if the ClientOnboarding record exists for the current user within the tenant
    client_onboarding, created = ClientOnboarding.objects.get_or_create(
        client=admin_user,
        tenant=tenant,  # Filter by tenant
        defaults={'trainers_onboarded': 0, 'students_onboarded': 0}
    )

    # Calculate the maximum number of forms to display
    max_forms= total
    remaining_forms = max_forms
    print(remaining_forms, "Remaining Forms to Onboard")

    
    UserFormSet = formset_factory(UserOnboardingForm, extra=1, max_num=max_forms, validate_max=True)

    if request.method == 'POST':
        print(request.user  )
        formset = UserFormSet(request.POST,form_kwargs={'tenant': tenant, 'user': request.user})
        print(request.user,"form la no display ")

        if formset.is_valid():
            for form in formset:
                user = form.save(commit=False)
                print(user,"lineeeeeeeeeee")
                 # or set a random password if you prefer
                user.save()

                role = form.cleaned_data.get('role')
                print(role,"jinreeeeeeeeeeeeee")    
                mentor=form.cleaned_data.get('mentor')
                print(mentor,"oooooooooooooooooooooooooo")
                if mentor:
                  try:
                    mentor_user = get_object_or_404(User, email=mentor)

        # Now use the mentor_user to fetch the related TrainerLogDetail
                    stud_mentor = get_object_or_404(TrainerLogDetail, trainer_name=mentor_user)
                  except TrainerLogDetail.DoesNotExist:
                    print(f"No mentor found with email: {mentor}")
                    continue  # Skip to the next form if the mentor doesn't exist
                else:
                    print("Mentor is not provided")
                    continue


                if role == 'trainer':
                    TrainerLogDetail.objects.create(
                        trainer_name=user,
                        onboarded_by=admin_user,
                        tenant=tenant,  # Associate with the tenant
                        no_of_asanas_created=0, 
                        created_at=timezone.now(),
                         updated_at=timezone.now(),
                        
                    )
                    # Update ClientOnboarding model
                    django_messages.success(request,"Trainer onboarded successfully")
                    client_onboarding.trainers_onboarded = F('trainers_onboarded') + 1
                else:
                  
                    StudentLogDetail.objects.create(
                        student_name=user,
                        added_by=admin_user,
                       mentor=stud_mentor,
                         created_at=timezone.now(),
                        updated_at=timezone.now(),
                        
                        tenant=tenant  # Associate with the tenant
                    )
                    # Update ClientOnboarding model
                    django_messages.success(request,"Student onboarded successfully")
                    client_onboarding.students_onboarded = F('students_onboarded') + 1

            # Save the updated counts to the database
            client_onboarding.save()
            remaining_forms -= len(formset)
            print(remaining_forms, "Remaining Forms after Onboarding")

            return render(request, 'users/Trainer_approval_Page.html',{'tenant':tenant})
        else:
            print(formset.errors)
            django_messages.error(request,"Form is not valid  ")

            print("formset is not valid")
    else:
        formset = UserFormSet()
        print("oh no form is not saved ")

    return render(request, 'users/onboarding_form.html', {'formset': formset,'tenant':tenant})
  except  Exception as e:
       print(e)
       django_messages.error(request,"An error occured ")
       return render(request,'users/error.html')





def user_login(request):
 
 try: 
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        print("Email:", email)
        
        user_obj = User.objects.filter(email=email).first()
        if user_obj is None:
           
            return render(request, "users/login.html")

        user = authenticate(username=user_obj.username, password=password)
        if user is not None:
            auth_login(request, user)  # Log in the user
            sweetify.success(request, 'You successfully logged in ')
            return redirect("role_based_dashboard")
        else:
            
            return render(request, "users/login.html")

    return render(request, "users/login.html")
 except IntegrityError:
     messages.error(request,'Already user exist')
 except Exception as e:
     return render(request,'error.html')




@login_required
def role_based_dashboard(request):
  try:
    if not request.user.is_authenticated:
        print("User not authenticated")
        return redirect('login')  # Redirect to login if not authenticated

    current_user = request.user
    print("Current user:", current_user)
    is_trainer = TrainerLogDetail.objects.filter(trainer_name=current_user).exists()
    is_student = StudentLogDetail.objects.filter(student_name=current_user).exists()
    is_client=Order.objects.filter(name=current_user).exists()
    print(is_client,"lllllllllllll")
    print(is_student,"kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
    # is_client = User.objects.filter(username=current_user).exists()
    # print(is_client,"loooooooooooooooooooooooooooo")

    print("is_trainer", is_trainer, "is_student", is_student)
    if is_trainer:
        try:
            get_trainer = TrainerLogDetail.objects.get(trainer_name=current_user,is_active=True)
            slug=get_trainer.tenant
            if get_trainer:
                client_name=get_trainer.onboarded_by
                print(client_name)
                get_tenant=Tenant.objects.filter(client_name=client_name).first()
                print(get_tenant,"oppppppppppppppppppppppppppp")
                get_status=get_tenant. is_active
                print(get_status,"poooooooooooooooooooooooooooo")
                if not get_status:
                    print("kannnnnnnnnnnnnni")
                    return render(request,"users/info.html")
                client_full_name=User.objects.get(username=client_name)
                subsciber_name=Order.objects.filter(name=client_full_name.first_name).first()
                print(subsciber_name,"pppppppppppppppppppppp")
                if subsciber_name:
                    get_subs=subsciber_name.subscription
                    print(get_subs)
                    get_status=get_subs.duration_in_months
                    get_start_date=subsciber_name.created_at
                    print(get_start_date)
                    expiration_date=get_start_date + timedelta(days=get_status)
                    print(expiration_date,"oooooooooooooooooooooooooooppppppppppppppp")
                    print(get_status)
                    print(timezone.now(),'sidfisd')
                    if timezone.now() >  expiration_date:
                        print("oops")
                       

                        return render(request,'users/error.html')
                    
                    else:
                        tenant = Tenant.objects.get(slug=slug)
                        return render (request,'users/view_trained.html',{
                             'tenant': tenant,
                                   
                        })
            else:
                            
                tenant = Tenant.objects.get(slug=slug)
                print(tenant,"trainer")
                return render(request, 'users/view_trained.html', {
                    'tenant': tenant,
                                   'slug': tenant.slug
        })




           
        except Exception as e:
              print("hello here is error ",e)
              
              return render(request, 'users/info_active.html'
              )

    elif is_student:
        get_student = StudentLogDetail.objects.get(student_name=current_user,is_active=True)
        slug=get_student.tenant
        if get_student:
                client_name=get_student.added_by
                print(client_name)
               
                get_tenant=Tenant.objects.filter(client_name=client_name).first()
                print(get_tenant,"oppppppppppppppppppppppppppp")
                get_status=get_tenant. is_active
                print(get_status,"poooooooooooooooooooooooooooo")
                if not get_status:
                    print("kannnnnnnnnnnnnni")
                    return render(request,"users/info.html")
                client_full_name=User.objects.get(username=client_name)
                subsciber_name=Order.objects.get(name=client_full_name.first_name)
                print(subsciber_name,"pppppppppppppppppppppp")
                if subsciber_name:
                    get_subs=subsciber_name.subscription
                    print(get_subs)
                    get_status=get_subs.duration_in_months
                    print(get_status)
                    get_start_date=subsciber_name.created_at
                    print(get_start_date)
                    expiration_date=get_start_date + timedelta(days=get_status)
                    print(expiration_date,"oooooooooooooooooooooooooooppppppppppppppp")
                    print(get_status)
                    print(timezone.now(),'sidfisd')
                    if timezone.now() >  expiration_date:
                        print("oops")
                        return render(request,'users/error.html')
                    
        else:
            return render(request, 'users/info_active.html'
              )
            

        
        print(slug,"lllllllllllllllllllllllllllllllllllll")
        tenant = Tenant.objects.get(slug=slug)
        print(tenant.slug,"lineeeeeeeeeeeeeee")
        print(tenant,"student")
        return render(request, 'users/user_view_asana.html', {
            'tenant': tenant,
            'slug': tenant.slug
        })

    elif is_client:
      
        print("here is the error")
        get_tenant_for_client = Tenant.objects.get(client_name=current_user,is_active=True)
        get_client=request.user
        tenant = get_tenant_for_client
        print(get_client)
        get_user=User.objects.get(username=get_client)
        get_order=Order.objects.filter(name=get_user.first_name).first()
        print(get_order)
        get_tenant=Tenant.objects.filter(client_name=current_user).first()
        print(get_tenant,"oppppppppppppppppppppppppppp")
        get_status=get_tenant. is_active
        print(get_status,"poooooooooooooooooooooooooooo")
        if not get_status:
           
            print("it get dele")
            print(get_tenant,"pppppppppp")
            print("kannnnnnnnnnnnnni")
            return render(request,"users/info.html")
        get_subs=get_order.subscription
        print(get_subs)
        get_status=get_subs.duration_in_months
        get_start_date=get_order.created_at
        print(get_start_date)
        expiration_date=get_start_date + timedelta(days=get_status)
        print(expiration_date,"pooooooooooooooooooooouih")

        print(get_status)
        if timezone.now()> expiration_date:
            print("oops")
            return redirect('renew')
        



        tenant = get_tenant_for_client

        print(tenant,"client")
        print(tenant.slug,"lineeeeeeeeeeeeeee")
        return render(request, "users/Trainer_approval_Page.html", {
            'tenant': tenant,
            'slug': tenant.slug
        })
    else:
        print("entered knowinmy part")
        get_knowinmy=User.objects.get(username =request.user)
        print(get_knowinmy,"ppppppppppppppppppppppppppp")
        
        return render(request,'users/organization_list.html',{

        })
  except Exception as e:
      print("error",e)
    
      return render(request,'users/error.html')

  
      
        # Check if the user is in StudentLog or TrainerLog
        
    

    # If the user is not authenticated and POST request is received

    # If GET request is received, render the login page
  



def log_out(request,slug=None):
    try:
        tenant = Tenant.objects.get(slug=slug)
        print(tenant,"linwe 543")
        auth.logout(request)  # Logout the user
        sweetify.success(request, "User logged out successfully", button="OK")
        
       
        if tenant :
            return redirect('home_slug',slug=slug)
        else:
            return redirect('home')  # Redirect to the normal home page if no tenant slug
    except Exception as e:
        # messages.error(request, 'An error occurred while logging out.')
        print(e)
        return redirect('home')  # Redirect to the home page in case of error

@user_passes_test(check_trainer   )
def view_trained(request,slug):

 try:

    # tenant = getattr(request, 'tenant', None)
    tenant = Tenant.objects.get(slug=slug) or getattr(request, 'tenant', None)
    print("tenant",tenant.slug)
    print(tenant,"Line 404") # Assuming tenant is set in middleware
    trained_asanas = Asana.objects.filter(created_by=request.user, tenant=tenant)
    print(trained_asanas,"line 426")
    print(request.user,"line 427")
    print(tenant.slug,"line 479")
   
    return render(request, "users/view_trained.html", {
        "trained_asanas": trained_asanas,
         'is_trainer': True,
        'tenant':tenant,    
        'slug':tenant.slug
    })
 except Exception as e:
      return render(request,'error.html')



@user_passes_test(check_trainer or check_student or check_knowinmy)
def view_posture(request, asana_id,slug):
  try:
    print(asana_id,"line no 575")
    tenant = Tenant.objects.get(slug=slug)
    print(tenant,"line 576") # Assuming tenant is set in middleware

    # Ensure the asana belongs to the tenant
    
    
    # Filter postures by asana and tenant
    postures = Posture.objects.filter(asana=Asana.objects.get(id=asana_id, tenant=tenant)).order_by('step_no')
    print(postures,"lineno 584")
   
    return render(request, "users/view_posture.html", {
        "postures": postures,
        'is_trainer': True,
        'tenant':tenant
    })
  except Exception as e:
       return render(request,'error.html')

class CreateAsanaView(UserPassesTestMixin, View):

    def test_func(self):
        print(self.request.user.groups.filter(name="Trainer").exists())
        return self.request.user.groups.filter(name="Trainer").exists()

    def get_max_forms(self,request,slug):
   
        trainee_name = request.user
        print(trainee_name,"ooooooooooooooooooooooooooo")

        tenant = Tenant.objects.get(slug=slug)
        # tenant = getattr(request, 'tenant', None)
        print(tenant,"line 459")
        print(slug,"line 460")  # Assuming tenant is set in middleware
        try:
            print(trainee_name,tenant)
            client_for_trainer = TrainerLogDetail.objects.filter(trainer_name=trainee_name, tenant=tenant.id).first()
            print(client_for_trainer,"line 465 client for trainer")
            if client_for_trainer:
                client = client_for_trainer.onboarded_by
                print(client,"line 467 client")
                no_of_asanas_created_by_trainee = client_for_trainer.no_of_asanas_created
                print(no_of_asanas_created_by_trainee,"line 468")
                client_name=User.objects.filter(username=client).first()
                print(client_name.first_name)
                transaction = Order.objects.filter(name=client_name.first_name, status='ACCEPT').first()
                print(transaction,"line 470")
                if transaction:
                    subscription = transaction.subscription
                    max_forms = subscription.permitted_asanas
                else:
                    max_forms = 0
                    no_of_asanas_created_by_trainee = 0
            else:
                max_forms = 0    
                no_of_asanas_created_by_trainee = 0
        except Exception as e:
            print(f"Exception occurred: {e}")
            capture_exception(e)
            max_forms = 0
            no_of_asanas_created_by_trainee = 0

        return max_forms, no_of_asanas_created_by_trainee

    def get(self, request,slug, *args, **kwargs):
     try:
        print(slug,"line 488")
        tenant = getattr(request, 'tenant', None)
        print(tenant,"line 488")  # Assuming tenant is set in middleware
        max_forms, no_of_asanas_created_by_trainee = self.get_max_forms(request,slug)

        print(max_forms,"line 493")

        AsanaCreationFormSet = formset_factory(AsanaCreationForm, extra=1, max_num=max_forms, validate_max=True, absolute_max=max_forms)

        if 'update' in request.GET:
            tenant =  Tenant.objects.get(slug=slug)
            print(tenant.slug,"line 641 ")
            print(tenant,"line in crud asana 641")
            asana_id = request.GET.get('asana_id')
            print(asana_id)
            asana = Asana.objects.get(id=asana_id, tenant=tenant)
            print(asana,"line 604")
            form = AsanaCreationForm(instance=asana)
            

            sweetify.success(request, "Choose type of PO", button="OK")
            return render(request, "users/update_asana.html", {
                'form': form,
                'asana_id': asana_id,
                'is_trainer': True,
                'tenant':tenant,
                'slug':tenant.slug
            })

        else:
            tenant =  Tenant.objects.get(slug=slug)
            formset = AsanaCreationFormSet()
            
            return render(request, "users/create_asana.html", {
                'formset': formset,
                'is_trainer': True,
                'enable': True,
                'tenant':tenant,
                'slug':tenant.slug
            })
     except Exception as e:
          sweetify.warning(request,'An error occured')
          return render(request,'users/create_asana.html')

    def post(self, request,slug, *args, **kwargs):
     
        tenant = getattr(request, 'tenant', None) or Tenant.objects.get(slug=slug)
        print(tenant,"line 518") # Assuming tenant is set in middleware
        max_forms, no_of_asanas_created_by_trainee = self.get_max_forms(request,slug)
        print(max_forms,"line 523")
 
        created_asanas_by_trainer = TrainerLogDetail.objects.get(trainer_name=request.user, tenant=tenant)
        remaining_forms = max_forms - no_of_asanas_created_by_trainee
        print(remaining_forms,"line 526")
        asana_id = request.POST.get('asana_id')
        print(asana_id,"line 638")
        if 'delete_asana' in request.POST :
            asana_id = request.POST.get('asana_id')
            asana = get_object_or_404(Asana, id=asana_id, tenant=tenant)
            created_asanas_by_trainer.no_of_asanas_created -= 1
            created_asanas_by_trainer.save()
            asana.delete()
            django_messages.success(request, "Asana deleted successfully")
            return redirect("view-trained",slug=tenant.slug if slug else '')

        if "asana_id" in request.POST:
            
            print(asana_id,"lollllllllllllll")
            asana = Asana.objects.get(id=asana_id,tenant=tenant)
            print(asana,"modskerjgekrj")
            
            form = AsanaCreationForm(request.POST, instance=asana)
            
            print(tenant.slug,"line 654")
            
            
            if form.is_valid():
                form.save()
                
                no_of_postures_for_asanas = form.cleaned_data['no_of_postures']
                existing_postures = Posture.objects.filter(asana=asana).order_by('step_no')
    
   
                if no_of_postures_for_asanas > existing_postures.count():
                    
                     for i, posture in enumerate(existing_postures, 1):
                        print("sjdje")
                        posture.name = "Step-" + str(i)
                        print("Step no is saved ")
                        posture.step_no = i
                        

                        posture.save()
        
        
                     for i in range(existing_postures.count() + 1, no_of_postures_for_asanas + 1):
                            Posture.objects.create(step_no=i, asana=asana,name="Step-" + str(i),tenant=tenant)
    
   
                else:
        
                    for i, posture in enumerate(existing_postures[:no_of_postures_for_asanas], 1):
                          print(existing_postures.count(),no_of_postures_for_asanas,"line no 723")
                          posture.step_no = i
                          posture.save()
        
        
                    postures_to_delete=existing_postures[no_of_postures_for_asanas:]
                    print(postures_to_delete,existing_postures.count(),no_of_postures_for_asanas,"line no 729")
                    for posture in postures_to_delete:
                        posture.delete()
                    
               
                
            django_messages.success(request, "Asana updated successfully")   
            return redirect("view-trained",slug=tenant.slug if slug else '')

           


        

       
        
        else:
            AsanaCreationFormSet = formset_factory(AsanaCreationForm, extra=1, max_num=max_forms, validate_max=True, absolute_max=max_forms)
            formset = AsanaCreationFormSet(request.POST)
            if formset.is_valid():
                print("entered          llllllllllll")
                for form in formset:
                    print("888888888888888")
                    if remaining_forms > 0:
                        print(remaining_forms,"line 561")
                        asana = form.save(commit=False)
                        asana.created_by = request.user
                        asana.tenant = tenant  # Ensure the tenant is set for the asana
                        asana.created_at = timezone.now()
                        asana.last_modified_at = timezone.now()
                        print("")
                        asana.save()

                        created_asanas_by_trainer.no_of_asanas_created += 1
                        created_asanas_by_trainer.created_at = timezone.now()
                        created_asanas_by_trainer.updated_at = timezone.now()
                        created_asanas_by_trainer.save()

                        for i in range(1, asana.no_of_postures + 1):
                            Posture.objects.create(name=f"Step-{i}", asana=asana, step_no=i, tenant=tenant)

                        no_of_asanas_created_by_trainee += 1
                        remaining_forms -= 1
                        print(remaining_forms, "line 579")
                        print(messages,"leeee")
                        
                        django_messages.success(request, "Asana created successfully")
                        return redirect("view-trained",slug=tenant.slug if slug else '')
                    else:
                        print("max-limit-of-asansa")
                        django_messages.error(request, "Exceed max limit of asanas")
                        return redirect("view-trained",slug=tenant.slug if slug else '')
                        break

                    
            else:
                return render(request, "users/create_asana.html", {
                    'formset': formset,
                    'is_trainer': True,
                    'tenant':tenant,
                    'slug':tenant.slug
                })
     
         

class CourseCreationView(UserPassesTestMixin, View):

    def test_func(self):
        return check_trainer(self.request.user)
    

    def get(self, request,slug, *args, **kwargs):
     try:
        tenant = Tenant.objects.get(slug=slug)
        print(tenant,"line 592")  # Assuming tenant is set in middleware
        course_id = request.GET.get('course_id')
        current_user = self.request.user
        
        
        print(course_id, "line 594x")
        if 'course_id' in request.GET:
            course =CourseDetails.objects.get( id=course_id, tenant=tenant)
            print(course_id,"loasjdkjn")
            form = CourseCreationForm(instance=course, user=self.request.user,tenant=tenant)
            return render(request, "users/update_course.html", {
                'form': form,
                'course_id': course_id,
                'is_trainer': True,
                'tenant':tenant,
                'slug':tenant.slug
            })
        else:
            form = CourseCreationForm(user=self.request.user,tenant=tenant)
            courses = CourseDetails.objects.filter(user=current_user, tenant=tenant)
           
            return render(request, "users/trainer_dashboard.html", {
                'form': form,
                'is_trainer': True,
                'courses': courses,
                 'slug':tenant.slug,
                
                'tenant':tenant
            })
     except Exception as e:
          print(e)
          return render (request,'users/error.html',)

    def post(self, request, slug,*args, **kwargs):
     try:
        tenant = Tenant.objects.get(slug=slug)
     
        print(tenant,"line 637")# Assuming tenant is set in middleware
        course_id = request.POST.get('course_id')
        print(course_id, "line 614")
        current_user = self.request.user

        if 'delete_course' in request.POST and 'course_id' :
            print(course_id,"line 931")
            courses_id= kwargs.get('course_id')
            course = get_object_or_404(CourseDetails, id=course_id, tenant=tenant)
            course.delete()
            django_messages.success(request, "Course deleted successfully")
            return redirect('create-course',slug=slug if slug else '')
        elif 'course_id'  in request.POST:
            course =CourseDetails.objects.get(id=course_id, tenant=tenant)
            print(course,"losdoajfskjdnvmnb")
            print(tenant,"line 639")
            form = CourseCreationForm(request.POST, instance=course, user=self.request.user,tenant=tenant)
            print("line 620")
            if form.is_valid():
                form.save()
                print(form.errors,"oooooooooooooooooooooooo")
                django_messages.success(request, "Course updated successfully")
                return redirect('create-course',slug=tenant.slug if slug else '')
                
               
            else:
                django_messages.error(request, "An error occured!")
                return render(request, "users/update_course.html", {
                    'form': form,
                    'course_id': course_id,
                    'is_trainer': True,

                    
                'tenant':tenant,
                'slug':tenant.slug
                })
     





        

                
    
        
        else:
            form = CourseCreationForm(request.POST, user=self.request.user,tenant=tenant)
            print(self.request.user,"line 661 to get user ")
            if form.is_valid():
                course = form.save(commit=False)
                course.user = request.user
                course.tenant = tenant  # Set the tenant for the course
                course.created_at = timezone.now()
                course.updated_at = timezone.now()
                course.save()  # Save the instance to the database
                form.save_m2m()  # Save many-to-many data
                django_messages.success(request, "Course created successfully")

                return redirect('create-course',slug=slug if slug else '')
            else:
                courses = CourseDetails.objects.filter(user=self.request.user)
                django_messages.error(request, "An error occured!")
                return render(request, "users/trainer_dashboard.html", {
                    'form': form,
                    'is_trainer': True,
                    'courses':courses,
                    'tenant':tenant
                })
     except Exception as e:
         django_messages.error(request, "An error occured!")
         return render(request,'error.html')


# @user_passes_test(check_student)
def home(request, slug=None):
  
        tenant = get_object_or_404(Tenant, slug=slug)
        current_user=request.user
        print(current_user,"line 1301")
        get_client=User.objects.get(email=current_user)
        get_transaction = False  # Default to False
        get_tenant = False  # Default to False
        if check_client(current_user):
                print(request.user,"pppppppppppppppppppppppp]]")
                print("it entered if part ")
                # Check if the client has made a transaction
                current_user=User.objects.filter(username=request.user).first()
                get_first_name=current_user.first_name
                
                get_transaction = Order.objects.filter(name=get_first_name).exists()  # Assuming Order model has a `user` field
                print(get_transaction,"hhhhhhhhhhhhhh")
               
               # Pass the necessary context to the template
                return render(request, "home_page.html", {
                
                'get_transaction': get_transaction,
                

                })
        else:
            return render(request, "home_page.html", {
              })


        

        subscriptions=Subscription.objects.all()
        print(slug,subscriptions)
        # Fetch subscriptions if tenant exists
       
        return render(request, "home_page.html",{'subscriptions':subscriptions,'get_tranasction':get_transaction})
    
@user_passes_test(check_student or check_client or check_trainer)
def staff_dashboard_function(request,slug):
 try:
    user = request.user
    tenant = getattr(request, 'tenant', None) or Tenant.objects.get(slug=slug)
    print(tenant,"from staff_dashboard")


    if user.groups.filter(name='Trainer').exists() or user.is_superuser:
        is_trainer = True
    else:
        is_trainer = False

    context = {
        'is_trainer': is_trainer,
        'tenant':tenant,
        'slug':tenant.slug
    }
    
    return render(request, "users/staff_dashboard.html", context)
 except Exception as e:
     
         return render(request,'error.html')


@user_passes_test(check_trainer)
def edit_posture(request,slug, posture_id):
 try:
    tenant =  Tenant.objects.get(slug=slug)
    print(tenant,"line 903")
    posture = get_object_or_404(Posture, id=posture_id, asana__tenant=tenant)
    
    if request.method == "POST":
        if "meta_details" in request.POST:
            form = EditPostureForm(request.POST, instance=posture)
            if form.is_valid():
                form.save()
        else:
            name = f"{posture.asana.name}_{posture.step_no}.csv"
            dataset = ast.literal_eval(request.POST["dataset"])
            dataset = pd.DataFrame(dataset)
            dataset = dataset.transpose()
            dataset.to_csv(f'./media/{name}', index=False, header=False)
            posture.dataset.name = name
            decoded_data = base64.b64decode(request.POST['snapshot'])
            with open(f"./media/images/{posture_id}.png", 'wb') as img_file:
                img_file.write(decoded_data)
            posture.snap_shot.name = f"./images/{posture_id}.png"
            posture.save()

    form = EditPostureForm(instance=posture)
    return render(request, "users/edit_posture.html", {
        "form": form,
        "posture": posture,
        'is_trainer': True,
        'tenant':tenant,
    })
 except Exception as e:
      return render(request,'error.html')








class StudentCourseMapView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return check_trainer(self.request.user)
    
    def get_enrollment_details(self,request,slug):
     try:
        trainee_name=self.request.user
        tenant = Tenant.objects.get(slug=slug)
        print(tenant,"line 759")
        print(slug,"slug must be printed") # Assuming tenant is set in middleware
        trainer_details = TrainerLogDetail.objects.filter(trainer_name=trainee_name, tenant=tenant).first()
        if trainer_details:
            client_name = trainer_details.onboarded_by
            print(client_name,"client name")
            enrolled_studs = list(StudentLogDetail.objects.filter(added_by=client_name, tenant=tenant))
            if enrolled_studs:
                student_names = [student.student_name for student in enrolled_studs]
                students = User.objects.filter(username__in=student_names)
                enrollment_details = EnrollmentDetails.objects.filter(user__in=students, tenant=tenant)
                print(enrollment_details,"lolllll")
                return enrollment_details
        return EnrollmentDetails.objects.none()  # Return an empty queryset if no students found
     except Exception as e:
          return render(request,'error.html')


    def get(self, request,slug, *args, **kwargs):
     try:
        print(slug,"line 916")
        user=self.request.user
        print(user,"line no 897")
        tenant =  Tenant.objects.get(slug=slug)
        print(tenant,"line no 918")
        enrollment_detailss = self.get_enrollment_details(user,slug)
        enrollment_details=EnrollmentDetails.objects.filter(created_by=self.request.user,tenant=tenant)
        print(enrollment_details,"line 958")
        print(enrollment_details,"line no 776")
        enrollment_id = request.GET.get('enrollment_id')
        
        if enrollment_id:
            enrollment = get_object_or_404(EnrollmentDetails, id=enrollment_id, tenant=tenant)
            form = StudentCourseMappingForm(instance=enrollment, user=self.request.user,tenant=tenant)
            return render(request, "users/update_student_course_form.html", {
                'form': form,
                'enrollment_id': enrollment_id,
                'tenant':tenant,
            })
        else:
            form = StudentCourseMappingForm(user=self.request.user,tenant=tenant)
            enrollment_detailss=EnrollmentDetails.objects.filter(created_by=self.request.user,tenant=tenant)
            print(enrollment_details,"line no 971")
            return render(request, "users/student_mapping.html", {
                'form': form,
                'enrollment_details': enrollment_details,
                'tenant':tenant
            })
     except Exception as e :
          return render(request,'users/error.html')

    
    def post(self, request,slug, *args, **kwargs):
     try:
        tenant = getattr(request, 'tenant', None) or Tenant.objects.get(slug=slug) # Assuming tenant is set in middleware
        enrollment_id = request.POST.get('enrollment_id')
        enrollment_details = self.get_enrollment_details(request.user,slug)




        if 'delete_course_map_form' in request.POST :
            enrollment = get_object_or_404(EnrollmentDetails, id=enrollment_id, tenant=tenant)
            enrollment.delete()
            django_messages.success(request, "Enrollment deleted successfully")
            return redirect('student-mapp-courses',slug=slug if slug else '')
            
            
        
        elif   enrollment_id or 'update_course_map_form' in request.POST:
            enrollment = get_object_or_404(EnrollmentDetails, id=enrollment_id, tenant=tenant)
            form = StudentCourseMappingForm(request.POST, instance=enrollment, user=request.user,tenant=tenant)
            if form.is_valid():
                form.save()
                django_messages.success(request, "Enrollment updated successfully")
               
                return redirect('student-mapp-courses',slug=slug if slug else '')
               
            else:
                django_messages.error(request, "An error occured!")
                return render(request, "users/student_mapping.html", {
                    'form': form,
                    'enrollment_details': enrollment_details,
                    'enrollment_id': enrollment_id,
                    'tenant':tenant,
                    'slug':tenant.slug
                })

        

        else:
            form = StudentCourseMappingForm(request.POST, user=request.user,tenant=tenant)
            if form.is_valid():
                enrollment = form.save(commit=False)
                enrollment.created_at = timezone.now()
                enrollment.updated_at = timezone.now()
                enrollment.tenant = tenant 
                enrollment.created_by=self.request.user # Set the tenant for the enrollment
                enrollment.save()
                form.save_m2m()
                django_messages.success(request, "Enrollment created successfully")
                return render(request, "users/student_mapping.html", {
                    'form': form,
                    'enrollment_details': enrollment_details,
                    'enrollment_id': enrollment_id,
                    'tenant':tenant,
                    'slug':tenant.slug
                })
            else:
                django_messages.error(request, "An error occured!")
                return render(request, "users/trainer_dashboard.html", {
                    'form': form,
                    'enrollment_id': enrollment_id,
                     'tenant':tenant,
                     'slug':tenant.slug
                })
     except Exception as e:
          print(e)
          django_messages.error(request, "An error occured!")

          return render(request,'users/error.html')






@login_required
@user_passes_test(check_student)
def user_view_asana(request,slug):
 try:
    tenant = Tenant.objects.get(slug=slug)  
    print(tenant,"line 781") # Assuming tenant is set in middleware
    current_user = request.user
    print(current_user," line 864")
    print(tenant.slug,"lojdfdsjkk")

    enrolled_student_to_courses = EnrollmentDetails.objects.filter(user=current_user, tenant=tenant)
    print(enrolled_student_to_courses,"line 1052")
    trainer_asanas = []
    if enrolled_student_to_courses.exists():
        all_courses = []
        for enrollment in enrolled_student_to_courses:
           all_courses.extend(enrollment.students_added_to_courses.all())
           print(all_courses,"line 1058")

      
        trainer_asanas.extend(all_courses)
   
    else:
        print("trainer asanas does not exist")
    
 
    return render(request, "users/user_view_asana.html", {
        "trainer_asanas": trainer_asanas,
        'tenant':tenant,
         
        "slug":tenant.slug
    })
 except Exception as e:
      return render(request,'error.html')



@login_required
@user_passes_test(check_student or check_knowinmy)
def user_view_posture(request,slug, asana_id):

    tenant = Tenant.objects.get(slug=slug)
    print(tenant,"line 886 in views.py ")
    try:
        
        postures = Posture.objects.filter(asana=get_object_or_404(Asana, id=asana_id, tenant=tenant)).order_by('step_no')
        print(postures,"line no 1008")
        return render(request, "users/user_view_posture.html", {
            "postures": postures,
            'is_trainer': True,
            'tenant':tenant,
            'slug':tenant.slug
        })
    except Exception as e:
        capture_exception(e)    
        return JsonResponse({"error": "An error occurred"}, safe=False)




# @login_required
# @user_passes_test(check_student)
# def get_posture(request, posture_id,tenant):
#     print("tenant",tenant)
#     if request.method == "GET":
#         tenant = Tenant.objects.get(tenant=tenant) # Assuming tenant is set in middleware
#         print(tenant,"line 1050")
#         posture = get_object_or_404(Posture, id=posture_id, asana__tenant=tenant)
#         link = str(posture.snap_shot.url)
#         return JsonResponse({"url": link})
#     else:
#         return JsonResponse({"error": "expected GET method"})
    

@login_required
@user_passes_test(check_student)
def get_posture(request,slug,posture_id):
 try:
    if request.method == "GET":
        tenant=Tenant.objects.get(slug=slug)
        print(tenant,"lin 1119")
        link = str(Posture.objects.get(id=posture_id,asana__tenant=tenant).snap_shot.url)
        return JsonResponse({"url":link})
    else:
        return JsonResponse({"error": "expected GET method"})
 except Exception as e:
      return render(request,'error.html')







@login_required
@user_passes_test(check_student)
def get_posture_dataset(request,slug):
 try:
    if request.method == "GET":
        
        tenant =Tenant.objects.get(slug=slug) 
        data={} # Assuming tenant is set in middleware
        posture_id = request.GET['posture_id']
        posture =  Posture.objects.get(id=posture_id,tenant=tenant) 
        dataset = pd.read_csv(posture.dataset.path, header=None)
        dataset = dataset.values.tolist()
        data["dataset"] = dataset
        data["snapshot"] = posture.snap_shot.url
        return JsonResponse(data)

    else:
        return JsonResponse(status=400, data={"error": "Bad request"})
 except Exception as e:
      return render(request,'error.html')



def subscription_plans(request):
 try:
    current_user=request.user
    print(current_user,"line 1030")
    

    subscriptions= Subscription.objects.all()
    print(subscriptions,"line 1009  ")
    return render(request,'home_page.html',{'subscriptions':subscriptions}) 
 except Exception as e:
      return render(request,'error.html')



@login_required
def trainer_dashboard(request, slug):
    try:
        current_user=request.user
        tenant = get_object_or_404(Tenant, client_name=request.user, slug=slug)
        trainers = TrainerLogDetail.objects.filter(tenant=tenant).select_related('trainer_name').first()
        email=trainers.trainer_name.email

        course_counts = {}
        enrollment_counts = {}
        trainer_courses = {}
        trainer_enrollments = {}

        for trainer in trainers:
            courses = CourseDetails.objects.filter(tenant=tenant, user=trainer.trainer_name)
            course_counts[trainer.trainer_name.id] = courses.count()
            trainer_courses[trainer.trainer_name.id] = courses
            
            enrollments = EnrollmentDetails.objects.filter(tenant=tenant, created_by=trainer.trainer_name).select_related('user')
            enrollment_counts[trainer.trainer_name.id] = enrollments.count()
            trainer_enrollments[trainer.trainer_name.id] = enrollments

        # Handle enable/disable action
        if request.method == "POST":
            action = request.POST.get('action')
            trainer_id = request.POST.get('trainer_id')
            trainer_to_update = trainers.filter(trainer_name__id=trainer_id).first()
            print(trainer_to_update,"ppppppppppppppppppppp")
            
            if trainer_to_update:
                if action == 'enable':
                    print("it got enabled")
                    send_mail(
                    subject=f"Message from {current_user}",
                    message="You got enabled in this website",
                    from_email='prabhaprasath07@gmail.com',
                    recipient_list=email,
               )

                    trainer_to_update.is_active = True
                elif action == 'disable':
                    print("it got disabled")
                    trainer_to_update.is_active = False
                    send_mail(
                    subject=f"Message from {current_user}",
                    message="You got disabled in this website.Contact your client",
                    from_email='prabhaprasath07@gmail.com',
                    recipient_list=email,
               )
                trainer_to_update.save()

        return render(request, 'users/trainers.html', {
            'trainers': trainers,
            'course_counts': course_counts,
            'enrollment_counts': enrollment_counts,
            'trainer_courses': trainer_courses,
            'trainer_enrollments': trainer_enrollments,
            'tenant': tenant,
        })
    except Exception as e:
        print("Error:", e)
        return render(request, 'users/error.html')
def enable_or_disable_user(request, slug, user_id):
    tenant = Tenant.objects.get(slug=slug)
    current_user = request.user
    user = User.objects.get(id=user_id)
    
    # Determine the user's group
    group_name = None
    if user.groups.filter(name='Trainer').exists():
        group_name = 'Trainer'
    elif user.groups.filter(name='Student').exists():
        group_name = 'Student'
    elif user.groups.filter(name='Client').exists():
        group_name = 'Client'
    else:
        return HttpResponse("User does not belong to a valid group", status=400)

    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return HttpResponse(f"Group '{group_name}' not found", status=404)

    # Enable or disable the user in the group
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'enable':
            if not user.groups.filter(name=group_name).exists():
                user.groups.add(group)
                return HttpResponse(f"User added to group: {group_name}")
            return HttpResponse(f"User is already enabled in group: {group_name}")
        elif action == 'disable':
            if user.groups.filter(name=group_name).exists():
                user.groups.remove(group)
                return HttpResponse(f"User removed from group: {group_name}")
            return HttpResponse(f"User is already disabled in group: {group_name}")

    return HttpResponse("Invalid action", status=400)


    


@login_required
def delete_trainer(request, trainer_id,slug):
 try:
    tenant=Tenant.objects.get(slug=slug)
    trainer = get_object_or_404(TrainerLogDetail, id=trainer_id,tenant=tenant)
    CourseDetails.objects.filter(tenant=tenant, user=trainer.trainer_name).delete()
    
    
    EnrollmentDetails.objects.filter(tenant=tenant, created_by=trainer.trainer_name).delete()
    
    trainer.delete()
   
    return redirect('trainer_dashboard',slug=tenant)
 except Exception as e:
      return render(request,'error.html')
      





@login_required
def edit_trainer(request, user_id,slug):
 try:
    print(user_id,"lllllllllllllllll")
    user = get_object_or_404(User, id=user_id)
    print(user,"ooooooooooooook")
    tenant=Tenant.objects.get(client_name=request.user,slug=slug)
    print(tenant.slug,"kkkkkkkkkkk")
    print(slug,"llllllllllllll")

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
           
            return redirect('trainer_dashboard', slug=slug)  # Adjust redirection as needed
    else:
        form = UserEditForm(instance=user)

    return render(request, 'users/edit_user.html', {'form': form, 'user': user,'slug':tenant.slug})
 except Exception as e:
      return render(request,'error.html')

   

@login_required
def  student_dashboard(request, slug):
 try:
    tenant = get_object_or_404(Tenant, client_name=request.user, slug=slug)


    
    enrollments = EnrollmentDetails.objects.filter(tenant=tenant).prefetch_related('students_added_to_courses', 'students_added_to_courses__asanas_by_trainer') 
    print(enrollments,"skdjfffffffffffffffffff")


    student_enrollment_map = {}
    for enrollment in enrollments:
        print(enrollment.user.id,"jdhbb")
        if enrollment.user not in student_enrollment_map:
            student_enrollment_map[enrollment.user] = []
        student_enrollment_map[enrollment.user].append(enrollment)
        print(student_enrollment_map,"oooooooooooooooooooooooo")
        
    print(enrollment.user,"kanis")
    get_stud=User.objects.filter(username=enrollment.user).first()
    print(get_stud.id)

    current_user=enrollment.user
    print(current_user,"oei cirrent")
    print(get_stud,"ooooopokohjhjhb")
    get_student=User.objects.filter(username=current_user)
    print(get_student,"ahsdgggggggggggdgg")
    if request.method == "POST":
            action = request.POST.get('action')
            student_id = request.POST.get('student_id')
            print(student_id,"idddddddddd")
            print(get_student,"line 1710")
            student_to_update = User.objects.filter(id=student_id).first()
            print(student_to_update,"llllllllllllllllllllllllllll")
            
            if student_to_update:
                if action == 'enable':
                    print("it got enabled")
                    student_to_update.is_active = True
                    student_to_update.save()
                elif action == 'disable':
                    print("it got disabled")
                    student_to_update.is_active = False
                    student_to_update.save()
                


    

    context = {
        'tenant': tenant,
        'student_enrollment_map': student_enrollment_map,
    }
    print(student_enrollment_map,"oooooooooooooooooo")
    return render(request, 'users/students.html', context)
 except Exception as e:
      print(e,"error")
      
      return render(request, 'users/error.html')



@login_required
def delete_student(request, student_id, slug):
 
    tenant = Tenant.objects.get(client_name=request.user,slug=slug)
    print(tenant,"line no 1215")
    try:
        student = StudentLogDetail.objects.get(id=student_id, tenant=tenant).delete()
        print(f"Found student: {student}")  

        
        print(f"Student name: {student.student_name}, Enrollments before deletion: {EnrollmentDetails.objects.filter(user=student.student_name).count()}")
        
        
        
        
        print(f"Deleted student: {student}")

        messages.success(request, 'Student and their enrollments deleted successfully.')
        return redirect('student_dashboard', tenant=tenant.slug)

    except StudentLogDetail.DoesNotExist:
        print("Student does not exist.")
       
        return redirect('student_dashboard', tenant=slug)
 
@login_required
def edit_user(request, user_id,slug):
 try:
    print(user_id,"ppppppppppppppppppppppppp")
    user = get_object_or_404(User, id=user_id)
    print(user,"sdihgggggggggggggggggg")
    tenant=Tenant.objects.get(client_name=request.user,slug=slug)
    print(tenant.slug,"kkkkkkkkkkk")
    print(slug,"llllllllllllll")

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
           
            return redirect('student_dashboard', slug=slug)  # Adjust redirection as needed
    else:
        form = UserEditForm(instance=user)

    return render(request, 'users/edit_user.html', {'form': form, 'user': user,'slug':tenant.slug})
 except Exception as e:
      return render(request,'error.html')






@login_required
@user_passes_test(check_client)
def register_organisation(request):
 try:
    print(request.user)
    

    if request.method == 'POST':
        
        
            # form = OrganisationForm(request.POST,user=request.user)
            form = OrganisationForm(request.POST)
            if form.is_valid():
                form.save()  
                print("Form is valid. Redirecting to login.")
                return redirect("home")
            else:
               print("Form is invalid. Errors:", form.errors)
    else:
             form = OrganisationForm(user=request.user)

    return render(request, 'users/register_organization.html', {'form': form})
 except Exception as e:
      print(e)
      return render(request,'users/error.html')











  

def client_dashboard(request, slug):
 try:
    current_user = request.user
    print(current_user, "line 1211")
    
    # Get tenant by slug
    tenant = get_object_or_404(Tenant, slug=slug)
    
    print(tenant, "line 1215")

    # Client onboarding info
    subscription_details = None
    client_onboarding = ClientOnboarding.objects.filter(tenant=tenant).first()
    trainers_onboarded_count = TrainerLogDetail.objects.filter(tenant=tenant).count()
    print(trainers_onboarded_count,"line 12222")
    
    # Subscription details
    
   
    get_order_subscription = Order.objects.filter(name=current_user).first()
    print(get_order_subscription,"line 1229")
    if get_order_subscription:
            subscription_details = get_order_subscription.subscription
            print(subscription_details, "line 1227")
   

    # Count students onboarded for the client
    students_onboarded_count = StudentLogDetail.objects.filter(tenant=tenant).count()
    print(students_onboarded_count,"line 1235")
    courses_count = CourseDetails.objects.filter(tenant=tenant).count()
    print(courses_count,"lineweiofjoeh")
    # Count enrollments done for the tenant
    enrollments_count = EnrollmentDetails.objects.filter(tenant=tenant).count() 
    print(enrollments_count,"line 1242")
    # Number of asanas created by trainers
   
    trainers = TrainerLogDetail.objects.filter(tenant=tenant)
    print(trainers,"line 3343434")
    total_asanas_created = trainers.aggregate(total_asanas=Sum('no_of_asanas_created'))['total_asanas'] or 0
    print(total_asanas_created,"line 1240")

    context = {
        'tenant': tenant,
        'trainers_onboarded': trainers_onboarded_count,
        'students_onboarded': students_onboarded_count,
        'subscription_details': subscription_details,
        'total_asanas_created': total_asanas_created,
        'courses_count':courses_count,
        'enrollments_count':enrollments_count
    }

    return render(request, 'users/client_dashboard.html', context)  
 except Exception as e:
      return render(request,'error.html')





def tenant_not_found(request):
    return render(request,"users/tenant_not_found.html")





def send_mail_page(request):
 try:
    context = {}
    print("Request method:", request.method)  # Debugging line to check request method

    if request.method == 'POST':
        name = request.POST.get('cf-name')
        email = request.POST.get('cf-email')
        message = request.POST.get('cf-message')

        if name and email and message:
            try:
                print("Sending email...")
                send_mail(
                    subject=f"Message from {name}",
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=['prabha2563@gmail.com'],
                fail_silently=False)
                context['result'] = 'Email sent successfully'
            except Exception as e:
                context['result'] = f'Error sending email: {e}'
        else:
            context['result'] = 'All fields are required'

    return render(request, "home_page.html", context)
 except Exception as e:
      return render(request,'error.html')




def home_slug(request, slug=None):
    try:
        subscriptions = Subscription.objects.all()  # Always retrieve subscriptions
        current_user = request.user
        
        get_transaction = False  # Default to False
        get_tenant = True  # Default to False

        if slug:
            tenant = get_object_or_404(Tenant, slug=slug)
            print(tenant, "line 1397")
            
            # Check if the user has an associated tenant
            tenant = Tenant.objects.get(slug=tenant)
            print(tenant,"ppppppppppppppppppppppppppppp")
            
            if check_client(current_user):
                print(request.user,"pppppppppppppppppppppppp]]")
                print("it entered if part ")
                # Check if the client has made a transaction
                current_user=User.objects.filter(username=request.user).first()
                get_first_name=current_user.first_name
                
                get_transaction = Order.objects.filter(name=get_first_name).exists()  # Assuming Order model has a `user` field
                print(get_transaction,"hhhhhhhhhhhhhh")
                get_tenant=Tenant.objects.get(client_name=current_user)
                print(get_tenant)

               # Pass the necessary context to the template
                return render(request, "home_page.html", {
                'subscriptions': subscriptions,
                'get_transaction': get_transaction,
                'get_tenant': get_tenant,


                })
            else:
                 return render(request, "home_page.html", {
                        'subscriptions': subscriptions,
                        'tenant':tenant,
                        'tenant':tenant.slug
                        
          })
        else:
            return render(request,"home_page.html",{
                'subscriptions':subscriptions,
              
                
            })


        
        # Render the normal home page if no slug is provided
       

    except Exception as e:
        print(e)
        return render(request, 'users/error.html')












@login_required
@user_passes_test(check_knowinmy)
def organization_list_view(request):
    try:
        organizations = Tenant.objects.all()

        if request.method == "POST":
            action = request.POST.get('action')
            tenant_id = request.POST.get('tenant_id')
            print(tenant_id,"ooooooooooooooooid")
            organization_to_update = organizations.filter(id=tenant_id).first()
            print("organization",organization_to_update)
            print(organization_to_update.is_active,"line 2010")

            if organization_to_update:
                if action == 'enable':
                    organization_to_update.is_active = True
                    print(organization_to_update.is_active,"line 2013")
                    organization_to_update.save()
                    print("got enabled")
                  
                elif action == 'disable':
                    organization_to_update.is_active = False
                    print(organization_to_update.is_active,"line 2018")
                    organization_to_update.save()
                    print("got diasnlad")
                   

        return render(request, 'users/organization_list.html', {'organizations': organizations})

    except Exception as e:
        print(f"Error: {e}")
        # messages.error(request, "An error occurred while processing the request.")
        return render(request, 'users/error.html')
@login_required
@user_passes_test(check_knowinmy)
def  asanas_view(request, tenant_id):
 try:
    tenant = get_object_or_404(Tenant, id=tenant_id)
    print(tenant,"pppppppppppppppppppppp")
    if tenant:
         get_deat=ClientOnboarding.objects.get(tenant=tenant)
         get_trainer_count=get_deat.trainers_onboarded
         get_stud_count=get_deat.students_onboarded
         get_client=get_deat.client
         print(get_client,"oooooooooooooooooooooooooooooo")
         get_tenant=Order.objects.get(name=get_client.first_name,status='ACCEPT')
         print(get_tenant,"looooooooooooooooooo")
         get_subs=get_tenant.subscription.name
         print(get_subs,"ouuuuuuuuuuuuuuuuu")
         get_name=User.objects.filter(email=get_client).first()
         get_order=Order.objects.filter(name=get_name.first_name).first()
         print(get_order,"popopop")
         get_subs=get_order.subscription
         print(get_subs,"ooooooooooooooo")
      
         get_asana_count=get_order.subscription.permitted_asanas
         get_no_of_persons_onboard=get_order.subscription.no_of_persons_onboard
         get_time=get_order.created_at
         get_status=get_subs.duration_in_months
         print(get_status,"ppppppppppppppppppppp")
         print(get_time,"oooooooooo")
         expiration_date=get_time + timedelta(days=get_status)
         print(expiration_date,"oooooooooooooooooooooooooooppppppppppppppp")

         print(get_trainer_count,get_stud_count,"ppppppppppppppppp")
    else:
        print("no tenant found")
   



    
    print(tenant,"loooooooooooooooo")
    asanas = Asana.objects.filter(tenant=tenant)
    asana_postures = []

    for asana in asanas:
    # Fetch all Posture objects related to the current asana
      postures = Posture.objects.filter(asana=asana)
   
      posture_images = [posture.snap_shot.url for posture in postures if posture.snap_shot]
      print(posture_images,"llllllllllll")
      asana_postures.append((asana, posture_images))
      flattened_asana_postures = [image for sublist in asana_postures for image in sublist]
      print(flattened_asana_postures,"line 2135")
      print(asana_postures,"array")  # Map asana to its posture images

    courses = CourseDetails.objects.filter(tenant=tenant).prefetch_related('asanas_by_trainer')

    return render(request, 'users/asanas_list.html', {
            'asanas': asanas,
               'tenant': tenant,
              'get_trainer_count': get_trainer_count,
              'get_stud_count': get_stud_count,
              'get_subs': get_subs,
              'courses': courses,
            'expiration_date': expiration_date,
             'asana_postures': asana_postures # Pass asana-posture mapping to the template
           })

 except Exception as e:
     return render(request, 'users/asanas_list.html')
     

@login_required
@user_passes_test(check_knowinmy)
def remove_asana_view(request, asana_id):
 try:
    asana = get_object_or_404(Asana, id=asana_id)

    if request.method == 'POST':
        asana.delete()  # Deleting the asana
        print("success")
        return redirect('organization_list')  # Redirect back to organization list or another relevant page

    return render(request, 'users/confirm_remove_asana.html', {'asana': asana})
 except Exception as e:
      return render(request, 'users/confirm_remove_asana.html')
     

@login_required
@user_passes_test(check_knowinmy)
def send_email_view(request, tenant_id):
 try:

    tenant = get_object_or_404(Tenant, id=tenant_id)
    if request.method == 'POST':
        subject = 'Query from Admin'
        message = request.POST.get('message')
        recipient = ['prabha2563@gmail.com']
        send_mail(subject, message, 'prabhaprasath07@gmail.com', recipient)
        return redirect('organization_list')
    return render(request, 'users/send_email.html', {'tenant': tenant})
 except Exception as e:
      return render(request, 'users/send_email.html')
@login_required
@user_passes_test(check_knowinmy)
def create_coupon_view(request, tenant_id):
 try:
    tenant = get_object_or_404(Tenant, id=tenant_id)
    subscriptions = Subscription.objects.all()  # Assuming you list subscriptions to choose from

    if request.method == 'POST':
        discounted_price = request.POST.get('discounted_price')
        subscription_id = request.POST.get('subscription_id')
        
        if not discounted_price or not subscription_id:
            return render(request, 'users/create_coupon.html', {'tenant': tenant, 'subscriptions': subscriptions, 'error': 'All fields are required.'})
        
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        # Create a coupon
        coupon = CouponCodeForNegeotiation.objects.create(
            user=tenant.client_name,
            subscription_for_coupon_code=subscription,
            discounted_price=discounted_price
        )
        
        # Send coupon code via email
        send_mail(
            subject='Your Coupon Code',
            message=f"Hello {tenant.organization_name},\n\nYour coupon code is {coupon.code}. You can use it for a discounted price of {coupon.discounted_price}.",
            from_email='prabhaprasath07@gmail.com',
            recipient_list=['prabha2563@gmail.com'],
        )
        print("send success")
        return redirect('organization_list')

    return render(request, 'users/create_coupon.html', {'tenant': tenant, 'subscriptions': subscriptions})
 except Exception as e:
      return render(request,'users/error.html')




@login_required
@user_passes_test(check_client)
def get_subscription_details_for_client(request,slug):
 try:
    print(slug)
    get_user=request.user
    get_deat=User.objects.filter(username=get_user).first()
    get_email=get_deat.first_name
    print(get_email,"ppppppppppppppppppppskfjdhkj")

    print(get_user,"pppppppppppp")
    tenant=Tenant.objects.filter(slug=slug).first()
    print(tenant,"puuuuuppyyyyyyy")
    get_order=Order.objects.filter(name=get_email).first()
    print(get_order,"popopop")
    get_subs=get_order.subscription
    get_asana_count=get_order.subscription.permitted_asanas
    get_no_of_persons_onboard=get_order.subscription.no_of_persons_onboard
    get_time=get_order.created_at
    get_status=get_subs.duration_in_months
    print(get_status,"ppppppppppppppppppppp")
    print(get_time,"oooooooooo")
    expiration_date=get_time + timedelta(days=get_status)
    print(expiration_date,"oooooooooooooooooooooooooooppppppppppppppp")



    get_client_onboardings=ClientOnboarding.objects.filter(tenant=tenant).first()
    if get_client_onboardings:
         get_count_stud=get_client_onboardings.students_onboarded
         get_count_trainer=get_client_onboardings.trainers_onboarded
         print(get_subs)
         return render (request,'users/show_subscription.html',{'slug':tenant.slug,'tenant':tenant,'get_order':get_order,'get_subs':get_subs,'get_asana_count':get_asana_count,'get_no_of_persons_onboard':get_no_of_persons_onboard,'get_count_stud':get_count_stud,'get_count_trainer':get_count_trainer,'expiration_date':expiration_date})
    else:
        return render (request,'users/show_subscription.html',{'slug':tenant.slug,'tenant':tenant,'get_order':get_order,'get_subs':get_subs,'get_asana_count':get_asana_count,'get_no_of_persons_onboard':get_no_of_persons_onboard,'get_count_stud':0,'get_count_trainer':0,'expiration_date':expiration_date})

   
 except Exception as e:
      print(e,"pppppppppppppppp")
      return render(request,'users/error.html')






@login_required
@user_passes_test(check_trainer)
def  student_dashboard_for_trainer(request, slug):
 try:
    tenant=Tenant.objects.get(slug=slug)

    current_user=request.user
    
    
    enrollments = EnrollmentDetails.objects.filter(created_by=current_user).prefetch_related('students_added_to_courses', 'students_added_to_courses__asanas_by_trainer')
    print(enrollments,"skdjfffffffffffffffffff")


    student_enrollment_map = {}
    for enrollment in enrollments:
        if enrollment.user not in student_enrollment_map:
            student_enrollment_map[enrollment.user] = []
        student_enrollment_map[enrollment.user].append(enrollment)
        print(student_enrollment_map,"oooooooooooooooooooooooo")

    context = {
        'tenant':tenant.slug,
        'tenant':tenant,
    
        'student_enrollment_map': student_enrollment_map,
    }
    print(student_enrollment_map,"oooooooooooooooooo")
    return render(request, 'users/student_info_to_trainer.html', context)
 except Exception as e:
      print(e,"pppppppppppppppppp")
      return render(request, 'users/error.html')
 







def renew_subscription(request):
    current_user=request.user
    get_tenant_for_client = Tenant.objects.get(client_name=current_user)
    
    tenant = get_tenant_for_client
    get_username=User.objects.get(username=current_user)
    get_first_name=get_username.first_name
    get_order=Order.objects.filter(name=get_first_name).first()
    print(get_order)
    get_order.delete()
    return render(request,'users/alert.html',{
                  'tenant': tenant,
            'slug': tenant.slug
            })
     








def dynamic_subscription_payment(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            # Extract form data
            no_of_persons_onboard = int(request.POST.get('no_of_persons_onboard', 0))
            permitted_asanas = int(request.POST.get('permitted_asanas', 0))
            duration_in_months = int(request.POST.get('duration_in_months', 0))

            # Calculate price
            price = (
                (permitted_asanas * 10) +
                (no_of_persons_onboard * 100) +
                (duration_in_months * 200)
            )
            print("Form data:", form.cleaned_data)  # Check cleaned data

            # Create a subscription instance without saving it yet
            form_data = form.save(commit=False)
            print(form,'kjjjjjjjjjj')
            print(form_data,"fuckk")
            form_data.price=price
            print(price)
            form.save()
            
             # Save the Subscription instance

            # Debugging: print the type and ID of the saved subscription
             # Should be a valid Subscription ID
            subscription_form = SubscriptionForm()
            subscription_form.fields['subscription_id'].initial = form_data.id
            request.session['subscription_id'] = form_data.id


            # Redirect to the payment view with the subscription ID
            print(form_data.id)
            
            return redirect('subscription-payment')
        
        else:
            print(form.errors)  # Print form errors for debugging
    else:
        form = SubscriptionForm()

    return render(request, 'users/subscription_detail.html', {'form': form})







@login_required
@user_passes_test(check_client)
def request_slug_change(request,slug=None):
    tenant = get_object_or_404(Tenant,  client_name=request.user)
    print(tenant,"pppppppppppppppppppp")
    print(tenant.slug,"ppppppppppppppjjjjjjjjjjjjjj")

    if request.method == "POST":
        form = SlugChangeRequestForm(request.POST)
        if form.is_valid():
            tenant = get_object_or_404(Tenant,  client_name=request.user)
            tenant.slug_change_requested = form.cleaned_data['slug_change_requested']
            tenant.slug_approved = False 
            print("iiiiiiiiiiiiiiiiiiiiiiiiiiii") # reset approval status
            tenant.save()
            # messages.success(request, "Slug change requested. Awaiting admin approval.")
            # Notify the admin here, if desired
            print(tenant.slug,"ppppppppppppppjjjjjjjjjjjjjj")
            context={
                'slug':tenant.slug,
            }
            return redirect('get-subs-for-client',tenant.slug)
    else:
        form = SlugChangeRequestForm()

    return render(request, 'users/request_slug_change.html', {'form': form, 'tenant': tenant})


@login_required
@user_passes_test(check_knowinmy)
def review_slug_changes(request):
    pending_tenants = Tenant.objects.filter(slug_change_requested__isnull=False, slug_approved=False)

    if request.method == "POST":
        tenant_id = request.POST.get("tenant_id")
        action = request.POST.get("action")
        tenant = get_object_or_404(Tenant, id=tenant_id)

        if action == "approve":
            tenant.slug = tenant.slug_change_requested
            tenant.slug_approved = True
            tenant.slug_change_requested = None
            tenant.save()
            django_messages.success(request,"Approved successfully")
            send_slug_change_notification(tenant,request)
            django_messages.success(request,"Approved successfully")
           
            # messages.success(request, f"Slug for {tenant.organization_name} approved and updated.")
        elif action == "reject":
            tenant.slug_change_requested = None
            django_messages.error(request,"Re   jected slug change")
            send_slug_change_reject_notification(tenant,request)
            
            # messages.warning(request, f"Slug change request for {tenant.organization_name} rejected.")
        tenant.save()

    return render(request, 'users/review_slug_changes.html', {'tenants': pending_tenants})


def send_slug_change_notification(tenant, request):
    print(tenant,"yyyyyyyyyyy 2236")
    subject = f"{tenant.organization_name} - Slug Changed"
    message = f"The slug has been updated to {tenant.slug}. You can now access it at this name"
    
    # Collect emails from trainers
    trainer_emails = TrainerLogDetail.objects.filter(tenant=tenant).values_list('trainer_name__email', flat=True)
    
    # Collect emails from students
    student_emails = StudentLogDetail.objects.filter(tenant=tenant).values_list('student_name__email', flat=True)

    # Get the current user (the client)
    current_user = request.user
    
    # Retrieve the client's email directly from the User model
    client_email = tenant.client_name.email if tenant.client_name else None  # Ensure there's a client

    # Combine the emails, ensuring uniqueness
    recipients = set(trainer_emails) | set(student_emails)
    
    # Add client email if it exists
    if client_email:
        recipients.add(client_email)

    # Sending the email
    recipient = ['prabha2563@gmail.com']
    send_mail(subject, message, 'prabhaprasath07@gmail.com', recipient)


def send_slug_change_reject_notification(tenant, request):
    print(tenant,"yyyyyyyyyyy 2236")
    subject = f"{tenant.organization_name} - Slug got rejected"
    message = f"The slug has been rejected to {tenant.slug}. You cannot now access it at this name"
    
    # Collect emails from trainers
    trainer_emails = TrainerLogDetail.objects.filter(tenant=tenant).values_list('trainer_name__email', flat=True)
    
    # Collect emails from students
    student_emails = StudentLogDetail.objects.filter(tenant=tenant).values_list('student_name__email', flat=True)

    # Get the current user (the client)
    current_user = request.user
    
    # Retrieve the client's email directly from the User model
    client_email = tenant.client_name.email if tenant.client_name else None  # Ensure there's a client

    # Combine the emails, ensuring uniqueness
    recipients = set(trainer_emails) | set(student_emails)
    
    # Add client email if it exists
    if client_email:
        recipients.add(client_email)

    # Sending the email
    recipient = ['prabha2563@gmail.com']
    send_mail(subject, message, 'prabhaprasath07@gmail.com', recipient)




@user_passes_test(check_client)
def subscription_change_request(request,slug=None):
    current_user=request.user
    tenant=Tenant.objects.filter(client_name=current_user).first()
    slug=tenant.slug
    

    print(current_user,"pppppppppppppppppppp")
    current_user_in_order=Order.objects.filter(name=current_user).first()
    # current_subs=current_user_in_order.subscription
    print(current_user_in_order,"pppppppppppppppppppp")
    if request.method == 'POST':
        form = SubscriptionChangeForm(request.POST)
        tenant=Tenant.objects.filter(client_name=current_user).first()
        slug=tenant.slug
        print(tenant,"ppppppppppppppp]")
       
        current_user_in_order=Order.objects.filter(name=current_user).first()
        # current_subs=current_user_in_order.subscription
        # print(current_user_in_order,current_subs,"pppppppppppppppppppp")
        if form.is_valid():
            subscription_request = SubscriptionChangeRequest.objects.create(
                tenant=request.user.tenant,  # Assuming the user has a related Tenant instance
                request_type=form.cleaned_data['request_type'],
                reason=form.cleaned_data['reason']
            )
            current_user=request.user
            current_user_in_order=Order.objects.filter(name=current_user).first()
            # current_subs=current_user_in_order.subscription
            # print(current_user_in_order,current_subs,"pppppppppppppppppppp")


            # messages.success(request, "Your request has been submitted.")
            return redirect('Trainer-approval',slug)
    else:
        form = SubscriptionChangeForm()
        
    
    return render(request, 'users/subscription_change_request.html', {'form': form,'current_user_in_order':current_user_in_order,})









def approve_subscription_change(request, request_id):
    subscription_request = get_object_or_404(SubscriptionChangeRequest, id=request_id)
    tenant = get_object_or_404(Tenant, id=subscription_request.tenant.id)


    if subscription_request.request_type == 'withdraw':
        tenant.is_active = False  # Disable the organization
        tenant.save()  # Save the tenant's active status
        messages.success(request, f"The organization '{tenant.organization_name}' has been disabled.")
    
    subscription_request.approved = True  # Mark the request as approved
    subscription_request.save()

    return redirect('list_subscription_requests')  # Redirect to the list of requests




def approve_subscription_change_by_knowinmy(request, request_id):
    subscription_request = get_object_or_404(SubscriptionChangeRequest, id=request_id)
    print(subscription_request,"pppppppppppppppppppppppppp")
    get_tenant_name=subscription_request.tenant
    get_client_name=Tenant.objects.filter(slug=get_tenant_name).first()
    print(get_client_name,"jzfdddddddddddd")
    get_user=get_client_name.client_name
    print(get_user,"pppppppppppppppppp")

   
   
    tenant=Tenant.objects.filter(client_name=get_user).first()
    get_fn=User.objects.get(username=get_user)
    get_name=get_fn.first_name
    print(get_name,"ppppppppppppppppsdifhsdjhjh")
    get_order=Order.objects.filter(name=get_name).first()
    print(get_order,"kkkkkkkkkkkkkkkka")
    print(tenant,"ooooooooooooooooooooo")

    get_subs=get_order.subscription
    print(get_subs,"llllllllllllllllll")
    action = request.POST.get('action')
    if action == 'approve':
        # Set tenant as inactive (disable organization access)
        tenant.is_active = False
        get_order.delete()


        tenant.save()
        send_email(
            subject="Subscription change request",
            message="Here your request to change in approval got approved",
            from_email="prabhaprasath07@gmail.com",
            recipient_list=[get_fn.email],
            

                   )
        print("hello")
        
    elif action == 'reject':
        # Set tenant as active (enable organization access)
        tenant.is_active = True
        tenant.save()
        send_email(
            subject="Subscription change request",
            message="Here your request to change in approval got rejected",
            from_email="prabhaprasath07@gmail.com",
            recipient_list=[get_fn.email],
            fail_silently=False,


                   )
        messages.success(request, f"The subscription for {tenant.client_name} has been enabled.")   

    
    subscription_request.delete()

    # Optionally, you can delete the request after processing
   

    return redirect('list_subscription_requests')  # Redirect back to the list of requests
@user_passes_test(check_knowinmy)
def list_subscription_requests(request):
    requests = SubscriptionChangeRequest.objects.filter(approved=False)  # Fetch all unapproved requests
    return render(request, 'users/subscription_requests.html', {'requests': requests})