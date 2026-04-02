import ast
import base64
import csv
import datetime
import json
import logging
import os
import time
from decimal import Decimal
from io import BytesIO

import pandas as pd
import razorpay
import sweetify
from django.conf import settings
from django.contrib import auth, messages
from django.contrib import messages as django_messages
from django.contrib.auth import authenticate, login, login as auth_login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage, send_mail
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Avg, Count, F, Sum
from django.dispatch import receiver
from django.forms import formset_factory
from django.http import FileResponse, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from import_export.formats.base_formats import XLSX
from openpyxl import load_workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sentry_sdk import capture_exception
from tablib import Dataset

from .forms import *
from .models import *
from .permissions import *
from .tables import *
from .tasks import *

logger = logging.getLogger(__name__)






def register(request):
 
    
 try:
    
    if request.method == "POST":

        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")

        try:
            validate_password(password)
        except ValidationError as e:
            django_messages.error(request, ', '.join(e.messages))
            return render(request, "users/user_register.html")

        user = User.objects.create_user(username=email,email=email,first_name=first_name,last_name=last_name,password=password)
        user.save()
        subject = "Welcome to Our Platform Knowinmy!"
        message = "Thank you for registering."
        from_email=settings.EMAIL_HOST_USER
        recipient_list = email
        print(email,"llllllllllllllllllllll")
    
    # Call the Celery task to send the email asynchronously
        send_email_task.delay(subject, message, recipient_list,from_email)
        
      
        return redirect('login')
    return render(request , "users/user_register.html")
 except IntegrityError:
     print("innnnnnnnn")
     django_messages.error(request,"A user with this email already exist")
     return render(request,'users/error_user.html')
 except  Exception as e:
      logger.exception(str(e))
      return render(request,'users/error.html')




@login_required
def   profile_view(request, slug=None):
    try:
      if slug:
        tenant = Tenant.objects.get(slug=slug)
        print(tenant,"lineeeeeeeeeeeee")
        print(tenant)
        if request.method == 'POST':
            # address = request.POST.get("address")
            # phone_number= request.POST.get("phone_number")
            # city = request.POST.get("city")
            # state= request.POST.get("state")

            print("hello world")
            profile, created = Profile.objects.get_or_create(user=request.user)
            form = ProfileForm(request.POST,request.FILES,  instance=profile)
            print(profile.address,profile.city,"oppppppppppppppppppppppp")

           
            print(profile.address,profile.image,"llllllllllllllll")
            if form.is_valid():
                form.save()
                print(profile.image,profile.address,"fom after save")
                return render(request, 'users/profile.html', {
            'form': form,
            'slug':tenant.slug,
            'tenant':tenant,
            'profile':profile
        })
                
               

                
               
        else:
            profile, created = Profile.objects.get_or_create(user=request.user)
            form = ProfileForm(instance=request.user)  
            return render(request, 'users/profile.html', {  
                'slug':tenant.slug,
                 'form': form,
            'tenant':tenant,
            'profile':profile
            })

           
           
            
       
    
    except Exception as e:
        logger.exception(str(e))
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
        logger.exception("update_profile failed: %s", e)
        return render(request, 'error.html')

def send_payment_invoice(request,order):
    user=request.user
    get_email=user.email

    subject = f"Payment Invoice for Order {order.provider_order_id}"
    message = f"""
    Dear Customer,

    Thank you for your payment. Here are the details of your transaction:

    Order ID: {order.provider_order_id}
   
    Amount: {order.amount} 
    Status: {order.status}
    Date: {order.created_at}

    We appreciate your business!

    Best regards,
       Knowinmy.
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
def subscription_payment(request):
 try:
    
    
    current_user=request.user
    print(current_user,"Current user")
    request.session['data'] = {
    'username': request.user.username,
    'email':request.user.email
   
}
    request.session.save()
    print(request.session['data'])  # Check after setting

   
   
   
   

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
            
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create(
            {"amount": int(amount * 100), "currency": "INR", "payment_capture": "1"}
        )
        order = Order.objects.create(
            subscription=subscription,
            user=current_user,
            name=name,
            amount=amount,
            provider_order_id=razorpay_order["id"]
        )
        order.save()
        group, _ = Group.objects.get_or_create(name='Client')
        if not current_user.groups.filter(name='Client').exists():
            current_user.groups.add(group)
            current_user.save()
        

        return render(
            request,
            "users/callback.html",
            {
                "callback_url": request.build_absolute_uri('/razorpay/callback/'),
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,
            },
        )
    
    else:
        print("entered elseeeeeeeeee")
        username = request.user
        print(username,"lollllll")
        get_only_username=User.objects.get(username=username)
        fname=get_only_username.first_name
        print(fname,"kkkkkkkk")
        
        subscription_id = request.session.get('subscription_id')
        print(subscription_id," linemnnnnn no 123")
      
       
        # price=request.session.get('subscription_price')
        # print(price,'jee')
        # print(subscription_id,"llllllllll")
        subscription = Subscription.objects.filter(id=subscription_id).first()
        print(subscription.price,"line no 123")
        if not subscription.price:
            subscription.save()
        print(subscription.duration_in_months,"oooooooooooooooooooooooooop")
    
        amount = Decimal(subscription.price)

        print(amount,"line nnooo")
       
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create(
            {"amount": int(amount * 100), "currency": "INR", "payment_capture": "1"}
        )
        order = Order.objects.create(
            subscription=subscription,
            user=current_user,
            name=fname,
            amount=amount,
            provider_order_id=razorpay_order["id"],
        )
        order.save()
        print("order savedjjjjj")
        group, _ = Group.objects.get_or_create(name='Client')
        if not current_user.groups.filter(name='Client').exists():
            current_user.groups.add(group)
            current_user.save()



        return render(
            request,
            "users/callback.html",
            {
                "callback_url": request.build_absolute_uri('/razorpay/callback/'),
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,
               
            },
        )   
        
        

    
 except Exception as e:
      logger.exception(str(e))
      return render(request,'users/payment_error.html')




@csrf_exempt
def callback(request):
    try:
        def verify_signature(response_data):
           
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
            if order.status == 'ACCEPT':
                return render(request, "users/success.html", {"order": order})
            order.payment_id = payment_id
            order.signature_id = signature_id
            order.created_at = timezone.now()
            order.is_active = True
            order.updated_at = timezone.now()
            order.save()

            if verify_signature(request.POST):
                order.status = 'ACCEPT'
                order.save()

                send_payment_invoice_task.delay(order.id)

                return render(request, "users/success.html", {"order": order})

            else:
                order.status = 'REJECT'
                order.save()
                print("FAILURE: Signature verification failed.")
                return render(request, "users/callback.html", {"status": 'REJECT'})

        else:
            # No signature present — do not modify order state without verification
            logger.warning("Razorpay callback received without signature for order_id: %s", request.POST.get("razorpay_order_id"))
            return render(request, "users/callback.html", {"status": 'REJECT'})

    except Exception as e:
        logger.exception(str(e))
        return render(request, "users/error.html")

# integrity error need to handle in this view - username must be unique


@login_required
def renew_subscription(request):
    user_name=request.user
    get_order=Order.objects.select_related('subscription').filter(user=user_name,is_active=True)
    
    print(get_order,"active orders")
    if get_order:
        for orders in get_order:
         print(orders,"order in loop")
         get_days=orders.subscription.duration_in_months
         print(orders.is_active,"pppp")
         print(get_days,"llllyyy")
        #  if orders.is_active == True  :
        #      subscription_end=orders.subscription.end_date  
        #      subscription_start=orders.subscription.start_date  
        #      get_day_to_send_email = (subscription_end - subscription_start).days / 2
        #      print(get_day_to_send_email, "Check get_day_to_send_email value")
        
        #      future_time_notify_email = timezone.now() + timedelta(days=get_day_to_send_email)
        #      print(future_time_notify_email, "line no 111 - Future notification time")
        #      print(orders.subscription.duration_in_months, "Duration in months")
            
             
        #      print(get_day_to_send_email,"line no nnnnnnnnnnnnnnnnnn111")
        #      print(orders.subscription.duration_in_months,"lllllll")
         
         if orders.is_active==True and orders.subscription.end_date<=timezone.now():
            print("hellommmmmmmmmmmmmm")
            subscription=orders.subscription.end_date    
            print(subscription,"linnnnnnnnnnnnnnnnne no 111")
            orders.is_active = False
            orders.save()
         if orders.is_active ==False and orders.subscription.end_date>=timezone.now():
                print(orders,"lineeeeeee")
                orders.is_active=True
                orders.save()
         

    else:
        print("no orders found ")


    
        
           



def generate_pdf_file(request):
#     get_payment_invoice.delay(get_email)
    # Create a BytesIO buffer
    buffer = BytesIO()
    p = canvas.Canvas(buffer,pagesize=letter)

    # Fetch data from session (if applicable)
    current_user=request.user
    # Example: Fetch orders from the database
    user=User.objects.get(username=current_user)
    orders=Order.objects.filter(user=user).first()
    print(orders)
    p.setFont("Helvetica-Bold", 20)
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 800, "Knowinmy")
    p.line(50, 770, 550, 770) 
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 750, "Payment Details")
    p.setFont("Helvetica", 12)
    
    y = 720
    p.drawString(100, y, f"Name: {orders.name}")
    p.drawString(100, y - 20, f"Amount: {orders.amount}")
    p.drawString(100, y - 40, f"Payment ID: {orders.payment_id}")
    # p.drawString(100, y - 40, f"Subscription : {orders}")
    p.line(50, y - 60, 550, y - 60)  # Horizontal line for separation

    # Footer Section
    y -= 80
    if y < 50:  # Start a new page if the content reaches the bottom
        p.showPage()
        y = 750

    p.setFont("Helvetica", 10)
    p.drawString(50, 40, "Thank you for choosing Knowinmy!")
    p.drawString(50, 25, "For inquiries, contact us at support@knowinmy.com or visit www.knowinmy.com")
    
    # Finalize the PDF
    p.showPage()
    p.save()

    # Retrieve the PDF content from the buffer
    buffer.seek(0)
    pdf_data = buffer.getvalue()
    buffer.close()

    # Return the PDF as an HTTP response
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="payment_invoice.pdf"'
    return response




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
            get_name_email=admin_user.email
            print(admin_user,"line 209")

          
            order_transaction = Order.objects.filter(
                user=admin_user,
                tenant=tenant,
                status='ACCEPT',
            ).first()
            print(tenant,admin_user,"line 288")
            print(order_transaction,"line 217")

            if not order_transaction:
                print("line no 232ijdsij")
                sweetify.warning(request, "No transaction found", button="OK")
                return render(request, 'users/Trainer_approval_Page.html')

            subscription = order_transaction.subscription
            no_of_persons_onboard_by_client_for_trainers_from_subscription = subscription.no_of_trainers
            no_of_persons_onboard_by_client_for_students_from_subscription = subscription.no_of_students

            no_of_persons_needed_to_onboard=ClientOnboarding.objects.filter(client=request.user,tenant=tenant).first()
            x=no_of_persons_needed_to_onboard.trainers_onboarded
            y=no_of_persons_needed_to_onboard.students_onboarded
            no_of_persons_onboard_by_client_trainers=no_of_persons_onboard_by_client_for_trainers_from_subscription-x
            no_of_persons_onboard_by_students=no_of_persons_onboard_by_client_for_students_from_subscription-y
            
            

            # Handle file upload
            uploaded_file = request.FILES.get('excel_file')
            if uploaded_file:
                admin_user_id = admin_user.id
                print(admin_user_id,"line 231")

                # Save the uploaded file temporarily
                file_path = default_storage.save(f'temp/{uploaded_file.name}', ContentFile(uploaded_file.read()))
                print(file_path,"llll")
                
                # Pass file path, admin user ID, and tenant information to the Celery task
                task=process_excel_file.delay(file_path, admin_user_id,  no_of_persons_onboard_by_client_trainers,no_of_persons_onboard_by_students, tenant.id)
                task_id=task.id
                print(task_id,"lllllllllllllllll")
                client_onboarding = ClientOnboarding.objects.get(client=admin_user, tenant=tenant)
                print("client onboarding is createed ",client_onboarding)
                get_count_of_trainers=client_onboarding.trainers_onboarded
                get_count_of_students=client_onboarding.students_onboarded
                print(get_count_of_students,get_count_of_trainers,"line 651")
                django_messages.success(request, "Users are being onboarded, you'll be notified once done.")
                
               



                    
                         
                    
                         
              


               
               
                
               
                
                
                
                
                
               
                
                
                




                
                
                

                
            else:
                
                django_messages.error(request, "No file uploaded!")

            return render(request, 'users/Trainer_approval_Page.html',{'tenant': tenant,"slug":tenant.slug})

        else:
            return render(request, 'users/Trainer_approval_Page.html',{'tenant': tenant,"slug":tenant.slug})

    except Exception as e:
        logger.exception(str(e))
       

        capture_exception(e)
        
       

       
        django_messages.error(request, "Error from our side ")
        return render(request,'users/error_msg.html')
@login_required
def csv_format(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="file.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(["username","email","first_name","last_name","roles","mentor"])
    

    return response   


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
    order_transaction = Order.objects.filter(user=admin_user, tenant=tenant, status='ACCEPT').first()
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
    no_of_persons_onboard_by_client_trainers = subscription.no_of_trainers
    no_of_persons_onboard_by_client_students = subscription.no_of_students

    print(no_of_persons_onboard_by_client_students,no_of_persons_onboard_by_client_trainers)
    client_onboardings, created = ClientOnboarding.objects.get_or_create(
                client=admin_user, tenant=tenant)
    no_of_persons_needed_to_onboard=ClientOnboarding.objects.filter(client=request.user,tenant=tenant).first()
    print(no_of_persons_needed_to_onboard,"l")
    x=no_of_persons_needed_to_onboard.trainers_onboarded
    y=no_of_persons_needed_to_onboard.students_onboarded
    print(x,y,"linee whwww")
    total1=no_of_persons_onboard_by_client_trainers-x
    total2=no_of_persons_onboard_by_client_students-y
    print(total1,total2,"line no 225")
    print(no_of_persons_onboard_by_client_students,no_of_persons_onboard_by_client_trainers, "Max Persons to Onboard")
    if total1 ==0 and  total2 ==0:
        max_forms=0
    elif total1 >0 or total2>0:
        max_forms=no_of_persons_onboard_by_client_trainers+no_of_persons_onboard_by_client_students
        # trainers_form=no_of_persons_onboard_by_client_trainers-x
        # students_form=no_of_persons_onboard_by_client_students-y
   




    # Check if the ClientOnboarding record exists for the current user within the tenant
    

    # Calculate the maximum number of forms to display
    
    remaining_forms = (no_of_persons_onboard_by_client_students+no_of_persons_onboard_by_client_trainers)-(y+x)
    # print(trainers_form,students_form,"form count of students and trainers")
    print(remaining_forms,max_forms, "Remaining Forms to Onboard")
    if remaining_forms <0:
        remaining_forms=0

    
    UserFormSet = formset_factory(UserOnboardingForm, extra=1, max_num=remaining_forms, validate_max=True)

    if request.method == 'POST':
        print(request.user  )
        formset = UserFormSet(request.POST,form_kwargs={'tenant': tenant, 'user': request.user})
        print(request.user,"form la no display ")

        if formset.is_valid():
            for form in formset:
                user = form.save(commit=False)
                print(user,"user from forms")
               
               
                print(user,"lineeeeeeeeeee")
                 # or set a random password if you prefer
                user.save()

                role = form.cleaned_data.get('role')
                print(role,"jinreeeeeeeeeeeeee")    
                mentor=form.cleaned_data.get('mentor')
                group, _ = Group.objects.get_or_create(name=role.capitalize())
                user.groups.add(group)
                print(mentor,"oooooooooooooooooooooooooo")
                if role == 'trainer' and not mentor:
                        
                    if x <total1:
                         print(x,no_of_persons_onboard_by_client_trainers)
                         TrainerLogDetail.objects.create(
                            trainer_name=user,
                            onboarded_by=admin_user,
                            tenant=tenant,
                            no_of_asanas_created=0, 
                            created_at=timezone.now(),
                            updated_at=timezone.now(),
                        )
                         client_onboardings.trainers_onboarded = F('trainers_onboarded') + 1
                         print(client_onboardings.trainers_onboarded,"line no 673")
                         client_onboardings.save()
                         default_password = User.objects.make_random_password()
                         user.set_password(default_password)
                         user.save()
                        
                         get_euser=User.objects.get(username=user)
                         get_email=get_euser.email
                         print(get_email,"loooo")
                         subject = "Welcome to Our Platform Knowinmy!"
                         message = (
                                  f"Hi usern\n"
                                   f"Welcome to Knowinmy! You onboard as a Trainer Your default password is: {default_password}\n\n"
                                             f"Please reset your password by clicking reset password :\n"
                                              f"Best regards,\nKnowinmy Team"

                                                

                              )
                         from_email=user_email.email
                         recipient_list = get_email
    
   
                         send_email_task.delay(subject, message, recipient_list,from_email)
        
                         continue
                    else:
                        print("No traines can be onboarded")
                        return render(request,"users/count.html")

                    
                        # Handle trainer without mentor
                        
                elif role == 'student' and mentor:
                        
                    try:
                        if y <total2:
                            # Fetch mentor from User
                            mentor_user = get_object_or_404(User, username=mentor)
                            stud_mentor = get_object_or_404(TrainerLogDetail, trainer_name=mentor_user)
                            
                            # Create StudentLogDetail
                            StudentLogDetail.objects.create(
                                student_name=user,
                                added_by=admin_user,
                                mentor=stud_mentor,
                                created_at=timezone.now(),
                                updated_at=timezone.now(),
                                tenant=tenant
                            )
                            client_onboardings.students_onboarded = F('students_onboarded') + 1
                            client_onboardings.save()
                            print(client_onboardings.students_onboarded,"line no 673")
                            get_euser=User.objects.get(username=user)
                            get_email=get_euser.email
                            print(user_email.email,"lineeeeeeee 874")
                            print(get_email,"loooo")
                            default_password = User.objects.make_random_password()
                            user.set_password(default_password)
                            user.save()
                            subject = "Welcome to Our Platform Knowinmy!"
                            message = (
                                  f"Hi usern\n"
                                   f"Welcome to Knowinmy! You onboard as a student  Your default password is: {default_password}\n\n"
                                             f"Please reset your password by clicking reset password :\n"
                                              f"Best regards,\nKnowinmy Team"

                                                

                           )
                            from_email=user_email.email
                            recipient_list = get_email
    
   
                            send_email_task.delay(subject, message, recipient_list,from_email)
                        else:
                            print("hello world no styd")
                            return render(request,"users/count.html")
                    except User.DoesNotExist:
                            print(f"No User found with email {mentor}. Skipping student {user.username}.")
                            continue  # Skip this student if mentor not found
                    except TrainerLogDetail.DoesNotExist:
                            print(f"No TrainerLogDetail found for mentor with email {mentor}. Skipping student {user.username}.")
                            continue  # Skip this student if mentor details not found

               
                
                  
                   
            # Save the updated counts to the database
           
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
       logger.exception(str(e))
       django_messages.error(request,"An error occured ")
       return render(request,'users/error.html')
 






def user_login(request):
 
 try: 
   
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        print("Email:", email)
        
        user_obj = User.objects.filter(email=email).first()
        print(user_obj,"line 660")
        if user_obj is None:
           
            return render(request, "users/login.html")

        user = authenticate(username=user_obj.username, password=password)
        if user is not None:
            auth_login(request, user)  # Log in the user
            django_messages.success(request, 'You successfully logged in ')
            return redirect("role_based_dashboard")
        else:
            
            django_messages.error(request, 'An error occured! ')
            return render(request, "users/login.html")
            

    return render(request, "users/login.html")
 except IntegrityError:
     messages.error(request,'Already user exist')
 except Exception as e:
     logger.exception("user_login failed: %s", e)
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
    is_client = current_user.groups.filter(name='Client').exists()
    is_admin = current_user.is_staff
    print(is_client,'client')
    print(is_admin,"lllllllllllll")
    print(is_student,"kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")

    print("is_trainer", is_trainer, "is_student", is_student)
    if is_trainer:
        try:
            get_trainer = TrainerLogDetail.objects.select_related('onboarded_by').get(trainer_name=current_user,is_active=True)
            print(get_trainer,"line 768")
            if not  get_trainer:
                 return render(request, 'users/info_active.html')
            
            # print(slug,"kk")
            if get_trainer:
                print("entered if part ")
                client_name=get_trainer.onboarded_by
                print(client_name)
                tenant=Tenant.objects.filter(client_name=client_name).first()
                print(tenant,"oppppppppppppppppppppppppppp")
                get_status=tenant. is_active
                print(get_status,"poooooooooooooooooooooooooooo")
                if not get_status:
                    print("kannnnnnnnnnnnnni")
                    return render(request,"users/info.html")
                tenant_sub = TenantSubscription.objects.filter(tenant=tenant, is_active=True).first()
                if tenant_sub:
                    if not tenant_sub.check_active():
                        return render(request, 'users/subs.html')
                    return render(request, 'users/view_trained.html', {'tenant': tenant})
                    
            else:
                            
                tenant = Tenant.objects.get(slug=slug)
                print(tenant,"trainer")
                return render(request, 'users/view_trained.html', {
                    'tenant': tenant,
                                
        })




           
        except Exception as e:
              logger.exception(str(e))
              return render(request, 'users/info_active.html')
              
             
              

    elif is_student:
     try:
        print("kanii")
        get_student = StudentLogDetail.objects.select_related('added_by').get(student_name=current_user,is_active=True)
        print(get_student,"kkkk")
        if not get_student:
             return render(request, 'users/info_active.html')

        
        print(get_student,"helllo worldd")
        slug=get_student.tenant
        if get_student:
                client_name=get_student.added_by
                print(client_name)
               
                tenant=Tenant.objects.filter(client_name=client_name).first()
                print(tenant,"oppppppppppppppppppppppppppp")
                get_status=tenant. is_active
                print(get_status,"poooooooooooooooooooooooooooo")
                if not get_status:
                    print("kannnnnnnnnnnnnni")
                    return render(request,"users/info.html")
                tenant_sub = TenantSubscription.objects.filter(tenant=tenant, is_active=True).first()
                if tenant_sub:
                    if not tenant_sub.check_active():
                        return render(request, 'users/subs.html')
                return render(request, 'users/user_view_asana.html', {'tenant': tenant})
                    
        else:
            return render(request, 'users/info_active.html'
              )
            

        
    
       
     except Exception as e:
              logger.exception(str(e))
              
              return render(request, 'users/info_active.html'
              )

    elif is_client:
      try:
        get_client=request.user
        print(request.user,"hrllllllo")
        get_tenant=False
        get_transaction=Order.objects.filter(user=current_user).first()
        print(get_transaction,"line 973hds")
        
     
        
        
        get_tenant_for_client = Tenant.objects.get(client_name=current_user,is_active=True)
        if not get_tenant_for_client:
            return render(request, 'users/info_active.html')


        get_client=request.user
        tenant = get_tenant_for_client
        print(get_client)
       

       
        tenant_sub = TenantSubscription.objects.filter(tenant=tenant, is_active=True).first()
        if not tenant_sub:
            return render(request, 'users/alert.html')
        if not get_tenant_for_client.is_active:
            return render(request, 'users/info.html')
        if not tenant_sub.check_active():
            return redirect('renew')
        



        tenant = get_tenant_for_client
        
        get_transaction=Order.objects.filter(user=current_user, tenant=tenant).exists()
        if get_transaction:
            get_tenant=True



        try:
          get_error = ErrorHandelingInUserUpload.objects.filter(tenant=tenant).latest('created_at')
          print(get_error, "line 1143")
          if get_error.celery_msg:
            if get_error.is_error:
                django_messages.error(request, f"Error: {get_error.celery_msg}")
            else:
                django_messages.success(request, get_error.celery_msg)

            
        except ErrorHandelingInUserUpload.DoesNotExist:
        # Handle the case where no error object exists
           pass

        

        
           

           
       
       
    

       
        
        print(get_tenant,"line 10222222222222")
       
        return render(request, "users/Trainer_approval_Page.html", {
            'tenant': tenant,
            'slug': tenant.slug,
            'get_transaction':get_transaction,
            'get_tenant':get_tenant

        })
      except  Exception as e:
          get_transaction=Order.objects.filter(user=current_user).exists()
          if get_transaction:
              get_tenant=True
          print(get_transaction,get_tenant,"line 973hds")
          
          
        
          logger.exception(str(e))
          return render (request,"home_page.html",{
               'get_transaction':get_transaction,
            'get_tenant':get_tenant
              
          })
    elif is_admin:
        return render(request,'users/organization_list.html',{

        })
    else:
        return render(request,'home_page.html')
        
  except Exception as e:
      logger.exception(str(e))
    
      return redirect('home')


  
      


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
        
        logger.exception(str(e))
        return redirect('home')  # Redirect to the home page in case of error

@login_required
@user_passes_test(check_trainer   )
def view_trained(request,slug):

 try:
    # tenant = getattr(request, 'tenant', None)
    tenant = Tenant.objects.get(slug=slug) or getattr(request, 'tenant', None)
    get_cl_name=tenant.client_name
    get_order=Order.objects.select_related('subscription').filter(user=get_cl_name, tenant=tenant, status='ACCEPT').first()
    print(get_order,get_cl_name,"line 404")
    if get_order:
        get_subs=get_order.subscription
        print(get_subs,"line 406")
        get_status=get_subs.permitted_asanas
        print(get_status,"line 408")


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
        'slug':tenant.slug,
        'get_status':get_status 
      
    })
 except Exception as e:
      logger.exception("view_trained failed: %s", e)
      return render(request,'users/error.html')



@login_required
@user_passes_test(check_any(check_trainer, check_student, check_knowinmy))
def view_posture(request, asana_id,slug):
  try:
    print(asana_id,"line no 575")
    tenant = Tenant.objects.get(slug=slug)
    print(tenant,"line 576")
    
    
    # Filter postures by asana and tenant
    postures = Posture.objects.filter(asana=Asana.objects.get(id=asana_id, tenant=tenant)).order_by('step_no')
    print(postures,"lineno 584")
   
    return render(request, "users/view_posture.html", {
        "postures": postures,
        'is_trainer': True,
        'tenant':tenant
    })
  except Exception as e:
       logger.exception("view_posture failed: %s", e)
       return render(request,'users/error.html')

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
        print(slug,"line 460") 
        try:
            print(trainee_name,tenant)
            client_for_trainer = TrainerLogDetail.objects.select_related('onboarded_by').filter(trainer_name=trainee_name, tenant=tenant.id).first()
            print(client_for_trainer,"line 465 client for trainer")
            if client_for_trainer:
                client = client_for_trainer.onboarded_by
                print(client,"line 467 client")
                no_of_asanas_created_by_trainee = client_for_trainer.no_of_asanas_created
                print(no_of_asanas_created_by_trainee,"line 468")
                transaction = Order.objects.select_related('subscription').filter(user=client, tenant=tenant, status='ACCEPT').first()
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
            logger.exception(str(e))
            capture_exception(e)
            max_forms = 0
            no_of_asanas_created_by_trainee = 0

        return max_forms, no_of_asanas_created_by_trainee

    def get(self, request,slug, *args, **kwargs):
     try:
        print(slug,"line 488")
        tenant = getattr(request, 'tenant', None) or Tenant.objects.get(slug=slug)
        print(tenant,"line 488")
        max_forms, no_of_asanas_created_by_trainee = self.get_max_forms(request,slug)

        print(max_forms,"line 493")

        AsanaCreationFormSet = formset_factory(AsanaCreationForm, extra=1, max_num=max_forms, validate_max=True, absolute_max=max_forms)

        if 'update' in request.GET:
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
          logger.exception(str(e))
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


@login_required
def home(request, slug=None):
  
        tenant = get_object_or_404(Tenant, slug=slug)
        current_user=request.user
        get_transaction = False  # Default to False
        get_tenant = False  # Default to False
        if check_client(current_user):
                print(request.user,"pppppppppppppppppppppppp]]")
                print("it entered if part ")
                # Check if the client has made a transaction
                current_user=request.user
                get_transaction = Order.objects.filter(user=current_user).exists()
                print(get_transaction,"hhhhhhhhhhhhhh")
                if get_transaction:
                    get_tenant=Tenant.objects.filter(client_name=current_user).exists()
                    print(get_tenant,)
                
               
               # Pass the necessary context to the template
                return render(request, "home_page.html", {
                
                'get_transaction': get_transaction,
                'get_tenant':get_tenant
                

                })
        else:
            return render(request, "home_page.html", {
              })
        



@login_required
@user_passes_test( check_client )        
def edit_mentor(request, slug):
    print(request.user,"line 1342")
    
    print("hello")
    tenant = get_object_or_404(Tenant, slug=slug) 
    try:
        instance = StudentLogDetail.objects.filter(tenant=tenant, added_by=request.user).first()
        print(instance,"line 1347")
    except StudentLogDetail.DoesNotExist:
        print(instance,"llllllllllllllllllllllllll")
        instance = None  # No instance to update; the form will create a new one if needed
    except Exception as e:
        logger.exception(str(e))
 # Assuming Tenant model is used for multi-tenancy

    if request.method == "POST":
        form = MentorEditForm(request.POST,instance=instance ,user=request.user ,tenant=tenant)
        if form.is_valid():
            print(form.data,"data")
            form.save()
            django_messages.success(request, "Mentor updated successfully!")
            
        else:
            print(form.errors,"lll errro")
            django_messages.error(request, "Failed to update mentor. Please check the form.")
    else:
        form = MentorEditForm( tenant=tenant,user=request.user )

    return render(request, 'users/mentor_edit.html', {'form': form, })
        
    
@login_required
@user_passes_test(check_any(check_student, check_client, check_trainer))
def staff_dashboard_function(request,slug):
 try:
    user = request.user
    profile=Profile.objects.get(user=user)
    print(profile,"lien 1677 in staff")
    tenant = getattr(request, 'tenant', None) or Tenant.objects.get(slug=slug)
    print(tenant,"from staff_dashboard")


    if user.groups.filter(name='Trainer').exists() or user.is_superuser:
        is_trainer = True
    else:
        is_trainer = False

    context = {
        'is_trainer': is_trainer,
        'tenant':tenant,
        'slug':tenant.slug,
        'profile':profile
    }
    
    return render(request, "users/staff_dashboard.html", context)
 except Exception as e:
         logger.exception("staff_dashboard_function failed: %s", e)
         return render(request,'error.html')


@user_passes_test(check_trainer)
def edit_posture(request,slug, posture_id):
 try:
    print(slug,"slug is")
    tenant =  Tenant.objects.get(slug=slug)
    print(tenant,"line 903")
    posture = get_object_or_404(Posture, id=posture_id, asana__tenant=tenant)
    print(posture,"posee")
    
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
      logger.exception(str(e))
      return render(request,'users/error.html')








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
          logger.exception(str(e))
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

    enrolled_student_to_courses = EnrollmentDetails.objects.prefetch_related('students_added_to_courses').filter(user=current_user, tenant=tenant)
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
      return render(request,'users/error.html')



@login_required
@user_passes_test(check_any(check_student, check_knowinmy))
def user_view_posture(request,slug, asana_id):

    tenant = Tenant.objects.get(slug=slug)
    print(tenant,"line 886 in views.py ")
    try:
        
        postures = Posture.objects.filter(asana=get_object_or_404(Asana, id=asana_id, tenant=tenant)).order_by('step_no')
        print(postures,"line no 1008")
        print(tenant.slug,"slug")
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
      return render(request,'users/error.html')







@login_required
@user_passes_test(check_student)
def get_posture_dataset(request,slug):
 try:
    if request.method == "GET":
        
        tenant =Tenant.objects.get(slug=slug) 
        data={} # Assuming tenant is set in middleware
        try:
            posture_id = int(request.GET['posture_id'])
        except (ValueError, KeyError):
            return JsonResponse(status=400, data={"error": "Invalid posture_id"})
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
        get_client_onboardings=ClientOnboarding.objects.get(client=current_user)

        tenant = get_object_or_404(Tenant, client_name=request.user, slug=slug)
        trainers = TrainerLogDetail.objects.filter(tenant=tenant).select_related('trainer_name')
       
        if not trainers:
            return render(request,'users/not_avail.html')
        trainers_email = trainers.first()
        email=trainers_email.trainer_name.email if trainers_email else ""

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
        # paginator = Paginator(trainer_enrollments, 10)  # 10 items per page
        # page_number = request.GET.get('page', 1)
        # page_obj = paginator.get_page(page_number)


        # Handle enable/disable action
        if request.method == "POST":
            action = request.POST.get('action')
            trainer_id = request.POST.get('trainer_id')
            print(trainer_id,'line 1700')
            trainer_to_update = trainers.filter(trainer_name__id=trainer_id).first()
            print(trainer_to_update,"ppppppppppppppppppppp")
            print(trainer_to_update.trainer_name.email,'jjjj')
            
            if trainer_to_update:
                if action == 'enable':
                    print("it got enabled")
                    send_email_task.delay(
                    subject=f"Message from {current_user}",
                    message="You got enabled in this website",
                   
                    recipient_list=trainer_to_update.trainer_name.email,
                     from_email=settings.EMAIL_HOST_USER,
               )
                
                    

                    trainer_to_update.is_active = True
                    trainer_to_update.save()
                    django_messages.success(request, "Trainer enabled   successfully!")
                    return redirect('trainer_dashboard',slug=slug if slug else '')
                elif action == 'disable':
                    print("it got disabled")
                    trainer_to_update.is_active = False
                    trainer_to_update.save()
                    send_email_task.delay(
                    subject=f"Message from {current_user}",
                    message="You got disabled in this website.Contact your client",
                    
                    recipient_list=trainer_to_update.trainer_name.email,
                    from_email=settings.EMAIL_HOST_USER,
               )
                    django_messages.success(request, "Trainer disabled successfully!")
                    return redirect('trainer_dashboard',slug=slug if slug else '')
                elif action == 'remove':
                    get_client_onboardings.trainers_onboarded-=1
                    get_client_onboardings.save()
                    trainer_to_update.is_active = False
                    print(get_client_onboardings.trainers_onboarded,"lllllllllllllllllll99999999")

                    trainer_to_update.delete()
                    send_email_task.delay(
                    subject=f"Message from {current_user}",
                    message="You got removed  from  this website.Contact your client",
                    
                    recipient_list=trainer_to_update.trainer_name.email,from_email=settings.EMAIL_HOST_USER)
                    django_messages.success(request, "Trainer removed  successfully!")
                    return redirect('trainer_dashboard',slug=slug if slug else '')
                elif action== "assign":
                 
                  trainer_to_update = trainers.filter(trainer_name__id=trainer_id).first()
                  print(trainer_to_update,"line 1740")
                  trainer_log=TrainerLogDetail.objects.get(trainer_name=trainer_to_update.trainer_name,tenant=tenant)
                     
                
                  form = MentorEditUserForm(request.POST, user=request.user, tenant=tenant)
                  
                  print(form,"form")
                  if form.is_valid():
                      student = form.cleaned_data['student_name']
                      student_user=User.objects.get(username=student)
                      student_log = StudentLogDetail.objects.get(student_name=student_user, tenant=tenant)
                      student_log.mentor = trainer_log
                      student_log.save()
                      django_messages.success(request, f"Student {student_user.username} assigned to {trainer_to_update.trainer_name.username} successfully!")
                      return render(request,'users/trainers.html',{'form':form,'tenant':tenant} )
                else:
                        form = MentorEditUserForm()
                        django_messages.error(request, "An error occured!")
                return render(request, 'users/trainers.html', {
                         'trainers': trainers,
                            'course_counts': course_counts,
                        'enrollment_counts': enrollment_counts,
                         'trainer_courses': trainer_courses,
                          'trainer_enrollments': trainer_enrollments,
                              'tenant': tenant,
                              'form':form
           
        })
               
        
                  

                   

                


                    
                

        return render(request, 'users/trainers.html', {
            'trainers': trainers,
            'course_counts': course_counts,
            'enrollment_counts': enrollment_counts,
            'trainer_courses': trainer_courses,
            'trainer_enrollments': trainer_enrollments,
            'tenant': tenant,
           
        })
    except Exception as e:
        logger.exception(str(e))
        return render(request, 'users/error.html')
@login_required
@user_passes_test(check_knowinmy)
def enable_or_disable_user(request, slug, user_id):
    tenant = get_object_or_404(Tenant, slug=slug)
    user = get_object_or_404(User, id=user_id)

    is_tenant_member = (
        TrainerLogDetail.objects.filter(trainer_name=user, tenant=tenant).exists()
        or StudentLogDetail.objects.filter(student_name=user, tenant=tenant).exists()
    )
    if not is_tenant_member:
        return HttpResponse("User does not belong to your tenant", status=403)

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
def student_dashboard(request, slug):
    try:
        current_user = request.user
        get_client_onboardings=ClientOnboarding.objects.get(client=current_user)
        
        get_email=current_user.email

        tenant = get_object_or_404(Tenant, client_name=request.user, slug=slug)

        # Fetch enrollments and students
        enrollments = EnrollmentDetails.objects.filter(tenant=tenant).prefetch_related(
            'students_added_to_courses', 'students_added_to_courses__asanas_by_trainer'
        )
        students = StudentLogDetail.objects.filter(tenant=tenant).select_related('student_name')

        if not students:
            return render(request, 'users/not_avail.html')

        # Group enrollments by user in Python — avoids 1 query per student in the loop
        from collections import defaultdict
        enrollment_map = defaultdict(list)
        for enrollment in enrollments:
            enrollment_map[enrollment.user_id].append(enrollment)

        student_enrollment_list = []
        for student in students:
            student_enrollment_list.append({
                'student': student,
                'enrollments': enrollment_map.get(student.student_name_id, [])
            })

        # Handle actions (enable/disable) if POST request
        if request.method == "POST":
            action = request.POST.get('action')
            student_id = request.POST.get('student_id')

            student_to_update = students.filter(
                    student_name__id=student_id, tenant=tenant
                ).first()
            paginator = Paginator(student_enrollment_list, 10)  # 10 items per page
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            

            if action == 'enable':
                student_to_update.is_active = True
                send_email_task.delay(
                    subject=f"Message from Client-{current_user}",
                    message="You got enabled in this website",
                   
                    recipient_list=[student_to_update.student_name.email],
                     from_email=settings.EMAIL_HOST_USER,
                )
                student_to_update.save()
                django_messages.success(request, "Trainer enabled  successfully!")
                return redirect('student_dashboard',slug=slug if slug else '')
            elif action == 'disable':
                student_to_update.is_active = False
                django_messages.success(request, "Trainer disabled  successfully!")
                
                send_email_task.delay(
                    subject=f"Message from Client-{current_user}",
                    message="You got disabled in this website",
                    
                    recipient_list=[student_to_update.student_name.email],
                     from_email=settings.EMAIL_HOST_USER,
                )
                student_to_update.save()
                return redirect('student_dashboard',slug=slug if slug else '')
                
            elif action =="remove":
                get_client_onboardings.students_onboarded-=1
                get_client_onboardings.save()
                student_to_update.is_active = False

                

           
                student_to_update.delete()
                django_messages.success(request, "Trainer removed  successfully!")
                

                
                print(StudentLogDetail.objects.all())
               
                send_email_task.delay(
                    subject=f"Message from Client-{current_user}",
                    message="You got removed  from this website",
                   
                    recipient_list=[student_to_update.student_name.email],
                     from_email=settings.EMAIL_HOST_USER,
                )
                return redirect('student_dashboard',slug=slug if slug else '')
                

            
            
            
           
               
               
        
        context = {
            'tenant': tenant,
            'student_enrollment_list': student_enrollment_list,
            'students': students,
           
        }
        # if request.method =='POST':
           
        #     action = request.POST.get('action')
        #     student_id = request.POST.get('student_id')
        #     get_stud=students.filter(
        #             student_name__id=student_id, tenant=tenant
        #         ).first()
            


        return render(request, 'users/students.html', context)

    except Exception as e:
        logger.exception(str(e))
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







def register_organisation(request):
 try:
   
    
   
    get_email=request.user.email
   
    
    print(request.method,"line 2389")
    if request.method == 'POST':
           

            domain_name = request.POST.get("domain_name")
            print(domain_name,"line 2392")
           
           

        
        
            # form = OrganisationForm(request.POST,user=request.user)
            form = OrganisationForm(request.POST)
            if form.is_valid():
                print(form.data,"line 2398")
                form.save()  
                print("Form is valid. Redirecting to login.")
                
                print("created successfully")
                tenant = Tenant.objects.filter(domain_name=domain_name).first()

                # Tenant now exists — link to the client's accepted Order and create TenantSubscription
                accepted_order = Order.objects.filter(
                    user=request.user, status='ACCEPT'
                ).order_by('-created_at').first()
                if accepted_order and tenant:
                    from datetime import timedelta
                    tenant_sub_end = accepted_order.created_at + timedelta(
                        days=accepted_order.subscription.duration_in_months
                    )
                    TenantSubscription.objects.get_or_create(
                        order=accepted_order,
                        defaults={
                            'tenant': tenant,
                            'plan': accepted_order.subscription,
                            'start_date': accepted_order.created_at,
                            'end_date': tenant_sub_end,
                            'is_active': True,
                        }
                    )
                    # Back-fill the tenant on the order record
                    accepted_order.tenant = tenant
                    accepted_order.save(update_fields=['tenant'])

                create=ClientOnboarding.objects.create(
                    tenant=tenant,
                    client=request.user,
                    trainers_onboarded =0 ,
                    students_onboarded=0

                )
                subject = "Welcome to Our Platform Knowinmy!"
                message = "You have successfully created your organization."
                recipient_list =get_email
                print(recipient_list,"lllllllllllllllllllll")
    
    # Call the Celery task to send the email asynchronously
                send_email_task.delay(subject, message, recipient_list, settings.EMAIL_HOST_USER)
        
                return redirect("role_based_dashboard")
            else:
               print(form.errors,"line 2409")
               
    else:
             print("it is in else part")
             form = OrganisationForm(user=request.user)
             print(form.errors,"oooooooooooo")

    return render(request, 'users/register_organization.html', {'form': form})
 except Exception as e: 
      logger.exception(str(e))
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
    
   
    get_order_subscription = Order.objects.filter(user=request.user, tenant=tenant).first()
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
      return render(request,'users/error.html')




def home_slug(request, slug=None):
    try:
        subscriptions = Subscription.objects.all()  # Always retrieve subscriptions
        current_user = request.user
        
        get_transaction = False  # Default to False
        get_tenant = False # Default to False

       
        tenant = get_object_or_404(Tenant, slug=slug)
        print(tenant, "line 1397")
            
            # Check if the user has an associated tenant
        tenant = Tenant.objects.get(slug=tenant)
        print(tenant,"ppppppppppppppppppppppppppppp")
            
        if check_client(current_user):
                print(request.user,"pppppppppppppppppppppppp]]")
                print("it entered if part ")
                # Check if the client has made a transaction
                current_user=request.user
                get_transaction = Order.objects.filter(user=current_user).exists()
                print(get_transaction,"hhhhhhhhhhhhhh")
                if get_transaction:
                    get_tenant=Tenant.objects.filter(client_name=current_user).exists()
                    
               
                
                print(get_tenant)

               # Pass the necessary context to the template
                return render(request, "home_page.html", {
                'subscriptions': subscriptions,
                'get_transaction': get_transaction,
                'tenant': tenant,
                'get_tenant':get_tenant


                })
        else:
                 return render(request, "home_page.html", {
                        'subscriptions': subscriptions,
                        'tenant':tenant,
                        'tenant':tenant.slug
                        
          })
       


        
        # Render the normal home page if no slug is provided
       

    except Exception as e:
        logger.exception(str(e))
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
        logger.exception(str(e))
        # messages.error(request, "An error occurred while processing the request.")
        return render(request, 'users/error.html')
@login_required
@user_passes_test(check_knowinmy)
def  asanas_view(request, tenant_id):
 print("entered ")
 try:
    tenant = get_object_or_404(Tenant, id=tenant_id)
    print(tenant,"pppppppppppppppppppppp")
    if tenant:
         print(tenant,"hello")
         get_deat=ClientOnboarding.objects.select_related('client').get(tenant=tenant)
         get_trainer_count=get_deat.trainers_onboarded
         get_stud_count=get_deat.students_onboarded
         get_client=get_deat.client  # already loaded via select_related, no extra query
         # single Order query with subscription JOINed
         get_order=Order.objects.select_related('subscription').filter(user=get_client, tenant=tenant, status='ACCEPT').first()
         print(get_order,"popopop")
         get_subs=get_order.subscription if get_order else None
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
    asanas = Asana.objects.filter(tenant=tenant).prefetch_related('related_postures')
    asana_postures = []

    for asana in asanas:
    # related_postures already prefetched — no extra query per asana
      postures = asana.related_postures.all()
   
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
    print(tenant,"linr 2433")
    get_client=tenant.client_name
    print(get_client,"line 2435jgfjgfk")

    if request.method == 'POST':
        subject = 'Query from Admin'
        message = request.POST.get('message')
        recipient_list = [get_client.email]
        send_email_task.delay(subject, message, recipient_list, from_email=settings.EMAIL_HOST_USER,)
        return redirect('organization_list')
    return render(request, 'users/send_email.html', {'tenant': tenant})
 except Exception as e:
      logger.exception(str(e))
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
       
        
        # Send coupon code via email
       
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
    tenant=Tenant.objects.filter(slug=slug).first()
    print(tenant,"puuuuuppyyyyyyy")
    get_order=Order.objects.filter(user=get_user, tenant=tenant).first()
   
    get_subs=get_order.subscription
    print(get_subs.no_of_trainers,"lllllllllllksjgkdsgkjksgjhjhlllllllllllllllllllllllllllllllllll")
    get_asana_count=get_order.subscription.permitted_asanas
    get_no_of_trainers_onboard=get_order.subscription.no_of_trainers
    get_no_of_students_onboard=get_order.subscription.no_of_students
    print( get_no_of_students_onboard,"lineeeeeeeeeeeee 2790000000000")
    get_time=get_order.created_at
    get_status=get_subs.duration_in_months
    print(get_status,"ppppppppppppppppppppp")
    print(get_time,"oooooooooo")
    expiration_date=get_time + timedelta(days=get_status)
    print(expiration_date,"kanishka")



    get_client_onboardings=ClientOnboarding.objects.filter(tenant=tenant).first()
    if get_client_onboardings:
         get_count_stud=get_client_onboardings.students_onboarded
         get_count_trainer=get_client_onboardings.trainers_onboarded
         print(get_subs)
         return render (request,'users/show_subscription.html',{'slug':tenant.slug,'tenant':tenant,'get_order':get_order,'get_subs':get_subs,'get_asana_count':get_asana_count,'get_no_of_trainers_onboard':get_no_of_trainers_onboard,'get_no_of_students_onboard':get_no_of_students_onboard,'get_count_stud':get_count_stud,'get_count_trainer':get_count_trainer,'expiration_date':expiration_date})
    else:
        return render (request,'users/show_subscription.html',{'slug':tenant.slug,'tenant':tenant,'get_order':get_order,'get_subs':get_subs,'get_asana_count':get_asana_count,'get_no_of_trainers_onboard':get_no_of_trainers_onboard,'get_no_of_students_onboard':get_no_of_students_onboard,'get_count_stud':0,'get_count_trainer':0,'expiration_date':expiration_date})

   
 except Exception as e:
      logger.exception(str(e))
      return render(request,'users/error.html')






@login_required
@user_passes_test(check_trainer)
def  student_dashboard_for_trainer(request, slug):
 try:
    tenant=Tenant.objects.get(slug=slug)
    get_client=tenant.client_name
    print(get_client,"line")

    current_user=request.user
    trainer=TrainerLogDetail.objects.get(trainer_name=current_user)
    print(trainer,"hello")
    students=StudentLogDetail.objects.filter(mentor=trainer)
    print(students,"lineeeeeeeeeeeeeeee")
    student=[]
    for student_name in students:
        print(student)
        student.append(student_name)
        print(student,"hhhhhhhhhhhh")
    
    
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
        'students':student,
    
        'student_enrollment_map': student_enrollment_map,
    }
    print(student_enrollment_map,"oooooooooooooooooo")
    return render(request, 'users/student_info_to_trainer.html', context)
 except Exception as e:
      logger.exception(str(e))
      return render(request, 'users/error.html')
 














@login_required
def dynamic_subscription_payment(request):
    current_user=request.user
    get_subs=Subscription.objects.filter(name=current_user.first_name).first()
    print(get_subs,"line 2489")
    if get_subs:
         print(get_subs.duration_in_months,"line 2491")
         form = SubscriptionForm(instance=get_subs)
         for field in form.fields.values():
            field.widget.attrs['readonly'] = 'readonly'
              # Make fields readonly
         if request.method == 'POST':
            
            get_subs.save()
            # Redirect to the payment page after submission
            return redirect('subscription-payment')  # Replace 'payment_page' with your URL name

         
         
        #  print(form,"ijjjjjjjj")
         return render(request, 'users/subscription_detail.html', {'form': form})
    else:
        pass

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Extract form data for price calculation
        no_of_students = int(request.POST.get('no_of_students', 0))
        no_of_trainers = int(request.POST.get('no_of_trainers', 0))
        permitted_asanas = int(request.POST.get('permitted_asanas', 0))
        duration_in_months = int(request.POST.get('duration_in_months', 0))

        # Calculate price
        price = (
            (permitted_asanas * 10) +
            (no_of_students * 50) +
            (no_of_trainers * 100) +
            (duration_in_months * 200)
        )

        # Return the calculated price as JSON
        return JsonResponse({'price': price})

    elif request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            # Extract form data
            no_of_students = int(request.POST.get('no_of_students', 0))
            no_of_trainers = int(request.POST.get('no_of_trainers', 0))
            permitted_asanas = int(request.POST.get('permitted_asanas', 0))
            duration_in_months = int(request.POST.get('duration_in_months', 0))

            # Calculate price
            price = (
                (permitted_asanas * 10) +
                (no_of_students * 50) +
                (no_of_trainers * 100) +
                (duration_in_months * 200)
            )
            no_of_persons_onboard = no_of_trainers + no_of_students

            # Create a subscription instance without saving it yet
            form_data = form.save(commit=False)
            form_data.price = price
            form_data.is_active=False
            form_data.no_of_persons_onboard = no_of_persons_onboard
            form_data.created_at=timezone.now()
            form_data.updated_at=timezone.now()
            form_data.description="Dynamic subscription"
            form_data.save()

            # Store data in session and redirect
            request.session['subscription_id'] = form_data.id
            request.session['subscription_price'] = price
            return redirect('home')

        else:
            print(form.errors)
            return render(request, "users/error.html")
    else:
        form = SubscriptionForm()

    return render(request, 'users/subscription_detail.html', {'form': form})
    
    






@login_required
@user_passes_test(check_client)
def request_slug_change(request,slug=None):
    current_user=request.user
    get_name=User.objects.get(username=current_user)
    get_email=get_name.email
    print(get_email,'lin')

    print(current_user,'line 2543')
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
            # asanas.save()
            # posture.save()
            # # courses.save()
            # # enroll.save()
            # trainerlog.save()
            # # studlog.save()
            # # onboard.save()
            # messages.success(request, "Slug change requested. Awaiting admin approval.")
            # Notify the admin here, if desired
            print(tenant.slug,"ppppppppppppppjjjjjjjjjjjjjj")
          
            send_email_task.delay(
                    subject=f"Message from  Knowinmy",
                    message="You are requested for slug change",
                   
                    recipient_list=[get_email],
                     from_email=settings.EMAIL_HOST_USER,
               )
            
            return redirect('get-subs-for-client',tenant.slug)
    else:
        form = SlugChangeRequestForm()

    return render(request, 'users/request_slug_change.html', {'form': form, 'tenant': tenant})

def review_slug_changes(request):
    pending_tenants = Tenant.objects.filter(slug_change_requested__isnull=False, slug_approved=False)

    if request.method == "POST":
        tenant_id = request.POST.get("tenant_id")
        action = request.POST.get("action")
        tenant = get_object_or_404(Tenant, id=tenant_id)

        print(f"Tenant ID: {tenant_id}, Tenant Slug: {tenant.slug}, Slug Change Requested: {tenant.slug_change_requested}")

        if action == "approve":
            
            old_slug = tenant.slug
            new_slug = tenant.slug_change_requested

            # Update the tenant's slug
            tenant.slug = new_slug
            tenant.domain_name=new_slug
            tenant.slug_approved = True
            tenant.slug_change_requested = None
            tenant.save()
            tenant.refresh_from_db()

            print(f"Approving slug change from '{old_slug}' to '{new_slug}'")

            # Update related models
            CourseDetails.objects.filter(tenant=tenant).update(tenant=tenant)
            EnrollmentDetails.objects.filter(tenant=tenant).update(tenant=tenant)
            TrainerLogDetail.objects.filter(tenant=tenant).update(tenant=tenant)
            StudentLogDetail.objects.filter(tenant=tenant).update(tenant=tenant)
            ClientOnboarding.objects.filter(tenant=tenant).update(tenant=tenant)
            Asana.objects.filter(tenant=tenant).update(tenant=tenant)
            Posture.objects.filter(tenant=tenant).update(tenant=tenant)

            # Notify and provide feedback
            django_messages.success(request, "Slug approved and updated successfully")
            send_slug_change_notification(tenant, request)

        elif action == "reject":

            tenant.slug_change_requested = None
            tenant.save()
            django_messages.error(request, "Slug change rejected")
            send_slug_reject_notification(tenant, request)

    return render(request, 'users/review_slug_changes.html', {'tenants': pending_tenants})



import pytz

from datetime import datetime
def     review_dynamic_subscription(request):
 try:
    pending_request_for_subscription = Subscription.objects.filter(active=False)


    if request.method == "POST":
        subscription_id = request.POST.get("subscription_id")
        action = request.POST.get("action")
        subscription = get_object_or_404(Subscription, id=subscription_id)

       
        if action == "edit":
            # Handle edits to subscription fields
           try:
                   subscription.no_of_trainers = int(request.POST.get("no_of_trainers", subscription.no_of_trainers))
                   subscription.no_of_students = int(request.POST.get("no_of_students", subscription.no_of_students))
                   subscription.duration_in_months = int(request.POST.get("duration_in_months", subscription.duration_in_months))
                   subscription.price = float(request.POST.get("price", subscription.price))
                   timezone = pytz.utc  # Replace with any other timezone if needed, e.g., pytz.timezone('Asia/Kolkata')

# Get the 'created_at' and 'updated_at' from the POST data (with defaults)
                   created_at_str = request.POST.get("created_at", subscription.created_at.isoformat())
                   updated_at_str = request.POST.get("updated_at", subscription.updated_at.isoformat())
                   subscription.created_at = datetime.fromisoformat(created_at_str).astimezone(timezone)
                   subscription.updated_at = datetime.fromisoformat(updated_at_str).astimezone(timezone)
                 

                   print(f"Before saving: {subscription.no_of_students}, {subscription.no_of_trainers}, {subscription.duration_in_months}, {subscription.price}, {subscription.created_at}, {subscription.updated_at}")

                   subscription.full_clean()
                   print(f"full clean: {subscription.no_of_students}, {subscription.no_of_trainers}, {subscription.duration_in_months}, {subscription.price}, {subscription.created_at}, {subscription.updated_at}")
                  
                   
                   print(f"AFTER refresh: {subscription.no_of_students}, {subscription.no_of_trainers}, {subscription.duration_in_months}, {subscription.price}, {subscription.created_at}, {subscription.updated_at}")

                   subscription.save(force_insert=False, force_update=True) # Save the updated subscription
                   print(f"AFTER saving: {subscription.no_of_students}, {subscription.no_of_trainers}, {subscription.duration_in_months}, {subscription.price}, {subscription.created_at}, {subscription.updated_at}")
         
             
           except (ValueError, TypeError) as e:
            django_messages.error(request, f"Type conversion failed: {e}")
            print(subscription.no_of_students, subscription.no_of_trainers, subscription.duration_in_months, subscription.price, "wooooooooooooo")
           except ValidationError as e:
            django_messages.error(request, f"Validation error: {e}")
            logger.exception(str(e))
           except Exception as e:

            django_messages.error(request, f"An unexpected error occurred: {e}")
            logger.exception(str(e))
            
        if action == "approve":
            subscription.active = False
            subscription.save()
          
            django_messages.success(request, "Subscription request accepted.")
            return redirect('organization_list')
        if action == "reject":
            subscription.delete()
            django_messages.error(request, "Subscription request rejected.")
            return redirect('organization_list')

       

    return render(request, 'users/review_ds.html', {'pending_request_for_subscription': pending_request_for_subscription})
 except Exception as e:
     logger.exception(str(e))






def send_slug_change_notification(tenant, request):
  try:
    print(tenant,"yyyyyyyyyyy 2236")
    subject = f"{tenant.organization_name} - Slug Changed"
    message = f"The slug has been updated to {tenant.slug}. You can now access it at this name"
    
    # Collect emails from trainers
    trainer_emails = TrainerLogDetail.objects.filter(tenant=tenant).values_list('trainer_name__email', flat=True)
    print(trainer_emails)
    
    # Collect emails from students
    student_emails = StudentLogDetail.objects.filter(tenant=tenant).values_list('student_name__email', flat=True)

    # Get the current user (the client)
    current_user = request.user
    
    # Retrieve the client's email directly from the User model
    
   
    # Combine the emails, ensuring uniqueness
    # Ensure trainer_emails and student_emails are not None
    trainer_emails = trainer_emails or []
    student_emails = student_emails or []
    recipient_list = list(set(email for email in trainer_emails if email) | set(email for email in student_emails if email))
    print("Recipient List:", recipient_list, type(recipient_list))

# Combine the sets and exclude any None values

   
    # Add client email if it exists
    
   
    # Sending the email
    recipient = ['velu@gmail.com']
    send_email_task.delay(subject, message,  recipient_list,settings.EMAIL_HOST_USER)
  except Exception as e:
      logger.exception(str(e))



def send_slug_reject_notification(tenant, request):
    print(tenant,"yyyyyyyyyyy 2236")
    subject = f"{tenant.organization_name} - Slug Change Request"
    message = f"The slug has not  updated to {tenant.slug}. "
    
    # Collect emails from trainers
    trainer_emails = TrainerLogDetail.objects.filter(tenant=tenant).values_list('trainer_name__email', flat=True)
    print(trainer_emails)
    
    # Collect emails from students
    student_emails = StudentLogDetail.objects.filter(tenant=tenant).values_list('student_name__email', flat=True)

    # Get the current user (the client)
    current_user = request.user
    
    # Retrieve the client's email directly from the User model
    client_email = tenant.client_name.email if tenant.client_name else None  # Ensure there's a client

    # Combine the emails, ensuring uniqueness
   # Ensure trainer_emails and student_emails are not None
    trainer_emails = trainer_emails or []
    student_emails = student_emails or []

# Combine the sets and exclude any None values
    recipient_list = tuple(set(email for email in trainer_emails if email) | set(email for email in student_emails if email))
    print("Recipient List:", recipient_list, type(recipient_list))

   
   

    # Sending the email
    recipient = ['prabha2563@gmail.com']
    send_email_task.delay(subject, message, recipient_list, settings.EMAIL_HOST_USER)







@user_passes_test(check_client)
def subscription_change_request(request,slug=None):
    current_user=request.user
    print(current_user,'line')
    get_name=User.objects.get(username=current_user)
    get_email=get_name.email
    tenant=Tenant.objects.filter(client_name=current_user).first()
    slug=tenant.slug
    

    print(current_user,"pppppppppppppppppppp")
    current_user_in_order=Order.objects.filter(user=request.user, tenant=tenant).first()
    # current_subs=current_user_in_order.subscription
    print(current_user_in_order,"pppppppppppppppppppp")
    if request.method == 'POST':
        form = SubscriptionChangeForm(request.POST)
        tenant=Tenant.objects.filter(client_name=current_user).first()
        slug=tenant.slug
        print(tenant,"ppppppppppppppp]")
       
        current_user_in_order=Order.objects.filter(user=request.user, tenant=tenant).first()
        # current_subs=current_user_in_order.subscription
        # print(current_user_in_order,current_subs,"pppppppppppppppppppp")
        if form.is_valid():
            subscription_request = SubscriptionChangeRequest.objects.create(
                tenant=request.user.tenant,  # Assuming the user has a related Tenant instance
                request_type=form.cleaned_data['request_type'],
                reason=form.cleaned_data['reason']
            )
            current_user=request.user
            current_user_in_order=Order.objects.filter(user=request.user, tenant=tenant).first()
            send_email_task.delay(
                    subject=f"Message from  Knowinmy",
                    message="You are requested for subscription change",
                 
                    recipient_list=[get_email],
                     from_email=settings.EMAIL_HOST_USER,
               )
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
    if subscription_request.request_type == 'change':
        tenant.is_active = True  # Disable the organization
        tenant.save() 
                
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
    get_order=Order.objects.filter(user=get_user, tenant=tenant).first()
    print(get_order,"kkkkkkkkkkkkkkkka")
    print(tenant,"ooooooooooooooooooooo")
    

   
   
    action = request.POST.get('action')
    if action == 'approve' and  subscription_request.request_type == 'withdraw':
        # Set tenant as inactive (disable organization access)
        tenant.is_active = False
        if get_order:
         get_subs=get_order.subscription 
         print(get_subs,"llllllllllllllllll")
         get_order.delete()
        


        tenant.save()
        send_email_task.delay(
            subject="Subscription change request",
            message="Here your request to change in approval got approved",
            
            recipient_list=[get_fn.email],
            from_email=settings.EMAIL_HOST_USER,
            

                   )
        print("hello")
        
    elif action == 'reject' and subscription_request.request_type == 'withdraw':
       
        tenant.is_active = True
        tenant.save()
        send_email_task.delay(
            subject="Subscription change request",
            message="Here your request to change in approval got rejected",
          
            recipient_list=[get_fn.email],
              from_email=settings.EMAIL_HOST_USER,
            fail_silently=False,


                   )
        messages.success(request, f"The subscription for {tenant.client_name} has been enabled.")   
    

    
    subscription_request.delete()
   
   

    return redirect('list_subscription_requests')  # Redirect back to the list of requests
@user_passes_test(check_knowinmy)
def list_subscription_requests(request):
    requests = SubscriptionChangeRequest.objects.filter(approved=False)  # Fetch all unapproved requests
    return render(request, 'users/subscription_requests.html', {'requests': requests})