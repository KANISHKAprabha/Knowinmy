from decimal import Decimal
import json
import os
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
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import  logout
from sentry_sdk import capture_exception
from django.views import View
# from bulkmodel.models import BulkModel

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



# for all the views need to handle permission denied ,viewsDoesNotExist,FieldError,ValidationError

def register(request):
    

    if request.method == "POST":

        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")

        user = User.objects.create_user(username=email,email=email,first_name=first_name,last_name=last_name,password=password)
        user.save()
        
      
        return redirect('login')
    return render(request , "users/user_register.html")




@login_required
def profile_view(request,slug):
    tenant=Tenant.objects.get(slug=slug)
    
    print(tenant,"line 87")
    
    return render(request,'users/profile.html',{'user': request.user,"slug":slug})

@login_required
@user_passes_test(check_client)
def subscription_payment(request):
    print("lidsofkehkfhsjdhfjsbjnb")
    current_user=request.user
    print(current_user,"jesfhggggggggggggggggggggggggggggggggg")
   
   

    if request.method == "POST":
        username = request.user
        get_only_username=User.objects.get(username=username)
        name=get_only_username.first_name
        print(name,"line no 111")
        subscription_id = request.POST.get("subscription_id")
        coupon_code = request.POST.get("coupon_code")
        subscription = Subscription.objects.get(id=subscription_id)
        
        amount = Decimal(subscription.price)
        discounted_amount_after_negotiation = amount

        if coupon_code:
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

        return render(
            request,
            "users/callback.html",
            {
                "callback_url": "http://" + "127.0.0.1:8000" + "/razorpay/callback/",
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,
            },
        )
    return render(request, "users/subscription_plans.html")



@csrf_exempt
def callback(request):
    # tenant = request.tenant  # Assuming the tenant is set in the middleware

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
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.created_at=timezone.now()
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
            print(admin_user,"line 209")

          
            order_transaction = Order.objects.filter(
                name=admin_user,
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

                sweetify.success(request, "Users are being onboarded, you'll be notified once done.", button="OK")
            else:
                sweetify.error(request, "No file uploaded!", button="OK")

            return render(request, 'users/Trainer_approval_Page.html',{'tenant': tenant,"slug":tenant.slug})

        else:
            return render(request, 'users/Trainer_approval_Page.html',{'tenant': tenant,"slug":tenant.slug})

    except Exception as e:
        print(e)
        capture_exception(e)
        return render(request, 'users/staff_dashboard.html',{'tenant': tenant,"slug":tenant.slug})
    


@login_required
@user_passes_test(check_superuser)   
def client_list(request):
    table=ClientTable(Order.objects.all())

    print(table,"print this tosd")
    return render(request,'users/client_table.html',{'table':table})










@login_required
def onboarding_view(request,slug):
    admin_user = request.user
    print(admin_user,"line no 281")
    tenant_name = Tenant.objects.get(slug=slug)
    
    tenant= tenant_name
    print(tenant,"line 276")
    # Assuming tenant is set in middleware

    # Filter the order by tenant and user
    order_transaction = Order.objects.filter(name=admin_user, status='ACCEPT').first()
    print(order_transaction,"llllllllllllllllllllllllllllllllll")

    print(tenant,admin_user,"line no 292")
    print(order_transaction,"likkk")

    if not order_transaction:
        tenant = Tenant.objects.get(slug=slug)
        sweetify.warning(request, "No transaction found", button="OK")
        print("No transaction found")
        print("hello")
        return render(request,'users/Trainer_approval_Page.html', {'slug':tenant.slug,'tenant':tenant})
    subscription = order_transaction.subscription
    print(subscription, "Subscription Details")
    no_of_persons_onboard_by_client = subscription.no_of_persons_onboard
    
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
        formset = UserFormSet(request.POST)

        if formset.is_valid():
            for form in formset:
                user = form.save(commit=False)
                 # or set a random password if you prefer
                user.save()

                role = form.cleaned_data.get('role')
                print(role,"jinreeeeeeeeeeeeee")
                mentor=form.cleaned_data.get('mentor')
                print(mentor,"oooooooooooooooooooooooooo")
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
                    client_onboarding.trainers_onboarded = F('trainers_onboarded') + 1
                else:
                    StudentLogDetail.objects.create(
                        student_name=user,
                        added_by=admin_user,
                        mentor=mentor,
                         created_at=timezone.now(),
                        updated_at=timezone.now(),
                        
                        tenant=tenant  # Associate with the tenant
                    )
                    # Update ClientOnboarding model
                    client_onboarding.students_onboarded = F('students_onboarded') + 1

            # Save the updated counts to the database
            client_onboarding.save()
            remaining_forms -= len(formset)
            print(remaining_forms, "Remaining Forms after Onboarding")
            return render(request, 'users/Trainer_approval_Page.html',{'tenant':tenant})

    else:
        formset = UserFormSet()

    return render(request, 'users/onboarding_form.html', {'formset': formset,'tenant':tenant})





def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        print("Email:", email)
        
        user_obj = User.objects.filter(email=email).first()
        if user_obj is None:
            print("jojg")
            return render(request, "users/login.html")

        user = authenticate(username=user_obj.username, password=password)
        if user is not None:
            auth_login(request, user)  # Log in the user
            return redirect("role_based_dashboard")
        else:
            
            return render(request, "users/login.html")

    return render(request, "users/login.html")

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
    print(is_student,"kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
    # is_client = User.objects.filter(username=current_user).exists()
    # print(is_client,"loooooooooooooooooooooooooooo")

    print("is_trainer", is_trainer, "is_student", is_student)
    if is_trainer:
        get_trainer = TrainerLogDetail.objects.get(trainer_name=current_user)
        slug=get_trainer.tenant
        print(slug,"loogjerojjjjjjjjjjjjjjjjjjjjjjjjjjjjj")
        tenant = Tenant.objects.get(slug=slug)
        print(tenant,"trainer")
        return render(request, 'users/view_trained.html', {
            'tenant': tenant,
            'slug': tenant.slug
        })

    elif is_student:
        get_student = StudentLogDetail.objects.get(student_name=current_user)
        slug=get_student.tenant
        print(slug,"lllllllllllllllllllllllllllllllllllll")
        tenant = Tenant.objects.get(slug=slug)
        print(tenant.slug,"lineeeeeeeeeeeeeee")
        print(tenant,"student")
        return render(request, 'users/user_view_asana.html', {
            'tenant': tenant,
            'slug': tenant.slug
        })

    else:
        print("here is the error")
        get_tenant_for_client = Tenant.objects.get(client_name=current_user)
        tenant = get_tenant_for_client
        print(tenant,"client")
        print(tenant.slug,"lineeeeeeeeeeeeeee")
        return render(request, "users/Trainer_approval_Page.html", {
            'tenant': tenant,
            'slug': tenant.slug
        })
  except:
      print("error")
      return render (request,"users/home.html")

        # Check if the user is in StudentLog or TrainerLog
        
    

    # If the user is not authenticated and POST request is received

    # If GET request is received, render the login page
  



def log_out(request,slug):
    try:
        tenant = Tenant.objects.get(slug=slug)
        print(tenant,"linwe 543")
        auth.logout(request)  # Logout the user
        sweetify.success(request, "User logged out successfully", button="OK")
        
       
        if hasattr(request, 'tenant') and request.tenant:
            return redirect('home-slug', slug=slug)
        else:
            return redirect('home-slug',slug=slug)  # Redirect to the normal home page if no tenant slug
    except Exception as e:
        # messages.error(request, 'An error occurred while logging out.')
        print(e)
        return redirect('home-slug',slug=slug)  # Redirect to the home page in case of error


@user_passes_test(check_trainer )
def view_trained(request,slug):

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


@login_required
@user_passes_test(check_trainer or check_student)
def view_posture(request, asana_id,slug):
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

                transaction = Order.objects.filter(name=client, status='ACCEPT').first()
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

        if asana_id  in request.POST:
            
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
               
                
                
            return render(request,"users/view_trained.html",{
                'form':form,
                'slug':tenant.slug,
                'asana_id': asana_id,
                'is_trainer': True,
              
                'tenant':tenant            })



        

        elif 'delete_asana' in request.POST:
            asana_id = request.POST.get('asana_id')
            asana = get_object_or_404(Asana, id=asana_id, tenant=tenant)
            
            created_asanas_by_trainer.no_of_asanas_created -= 1
            created_asanas_by_trainer.save()
            asana.delete()
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
                        return redirect("view-trained",slug=tenant.slug if slug else '')
                    else:
                        print(formset.errors,"error in formset")
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
        tenant = Tenant.objects.get(slug=slug)
        print(tenant,"line 592")  # Assuming tenant is set in middleware
        course_id = request.GET.get('course_id')
        current_user = self.request.user
        mentor=StudentLogDetail.objects.filter(mentor=self.request.user)
        
        print(course_id, "line 594x")
        if course_id:
            course = get_object_or_404(CourseDetails, id=course_id, tenant=tenant)
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

    def post(self, request, slug,*args, **kwargs):
        tenant = Tenant.objects.get(slug=slug)
        print(tenant,"line 637")# Assuming tenant is set in middleware
        course_id = request.POST.get('course_id')
        print(course_id, "line 614")
        current_user = self.request.user




        if 'delete_course' in request.POST and course_id :
            courses_id= kwargs.get('course_id')
            course = get_object_or_404(CourseDetails, id=course_id, tenant=tenant)
            course.delete()
            return redirect('create-course',slug=slug if slug else '')


        if  'update_course' in  request.POST:
            course = get_object_or_404(CourseDetails, id=course_id, tenant=tenant)
            print(tenant,"line 639")
            form = CourseCreationForm(request.POST, instance=course, user=self.request.user,tenant=tenant)
            print("line 620")
            if form.is_valid():
                form.save()
                return redirect('view-trained',slug=tenant.slug if slug else '')
                
               
            else:
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

                return redirect('create-course',slug=slug if slug else '')
            else:
                courses = CourseDetails.objects.filter(user=self.request.user)
                return render(request, "users/trainer_dashboard.html", {
                    'form': form,
                    'is_trainer': True,
                    'courses':courses,
                    'tenant':tenant
                })


# @user_passes_test(check_student)
def home(request, slug=None):
    if slug:
        tenant = get_object_or_404(Tenant, slug=slug)
        # Fetch subscriptions if tenant exists
        subscriptions = Subscription.objects.filter(tenant=tenant)
        return render(request, "users/home.html", {'subscriptions': subscriptions, 'tenant': tenant})
    else:
        # Render the normal home page if no slug is provided or tenant does not exist
        return render(request, "users/home.html")

@user_passes_test(check_student or check_client or check_trainer)
def staff_dashboard_function(request,slug):
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

@user_passes_test(check_trainer)
def edit_posture(request,slug, posture_id):
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







class StudentCourseMapView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return check_trainer(self.request.user)
    
    def get_enrollment_details(self,request,slug):
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

    def get(self, request,slug, *args, **kwargs):
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
    
    def post(self, request,slug, *args, **kwargs):
        tenant = getattr(request, 'tenant', None) or Tenant.objects.get(slug=slug) # Assuming tenant is set in middleware
        enrollment_id = request.POST.get('enrollment_id')
        enrollment_details = self.get_enrollment_details(request.user,slug)




        if 'delete_course_map_form' in request.POST :
            enrollment = get_object_or_404(EnrollmentDetails, id=enrollment_id, tenant=tenant)
            enrollment.delete()
            return render(request, 'users/student_mapping.html',{'tenant':tenant})
        
        elif   enrollment_id or 'update_course_map_form' in request.POST:
            enrollment = get_object_or_404(EnrollmentDetails, id=enrollment_id, tenant=tenant)
            form = StudentCourseMappingForm(request.POST, instance=enrollment, user=request.user,tenant=tenant)
            if form.is_valid():
                form.save()
                return render(request, "users/student_mapping.html", {
                    'form': form,
                    'enrollment_id': enrollment_id,
                    'tenant':tenant,
                    'slug':tenant.slug
                })
            else:
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
                return render(request, "users/student_mapping.html", {
                    'form': form,
                    'enrollment_details': enrollment_details,
                    'enrollment_id': enrollment_id,
                    'tenant':tenant,
                    'slug':tenant.slug
                })
            else:
                return render(request, "users/trainer_dashboard.html", {
                    'form': form,
                    'enrollment_id': enrollment_id,
                     'tenant':tenant,
                     'slug':tenant.slug
                })





@login_required
@user_passes_test(check_student)
def user_view_asana(request,slug):
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
    print(trainer_asanas,"linr 1062")
    return render(request, "users/user_view_asana.html", {
        "trainer_asanas": trainer_asanas,
        'tenant':tenant,
         
        "slug":tenant.slug
    })


@login_required
@user_passes_test(check_student)
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
    if request.method == "GET":
        tenant=Tenant.objects.get(slug=slug)
        print(tenant,"lin 1119")
        link = str(Posture.objects.get(id=posture_id,asana__tenant=tenant).snap_shot.url)
        return JsonResponse({"url":link})
    else:
        return JsonResponse({"error": "expected GET method"})







@login_required
@user_passes_test(check_student)
def get_posture_dataset(request,slug):
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


def subscription_plans(request):
    current_user=request.user
    print(current_user,"line 1030")
    if current_user:

        subscriptions= Subscription.objects.all()
        print(subscriptions,"line 1009  ")
        return render(request,'users/subscription_plans.html',{'subscriptions':subscriptions}) 





@login_required
def trainer_dashboard(request, slug):
    tenant = get_object_or_404(Tenant, client_name=request.user, slug=slug)

    trainers = TrainerLogDetail.objects.filter(tenant=tenant).select_related('trainer_name').prefetch_related('trainer_name__onboard_traines_by')
    print(trainers,"linee   ")
    
    course_counts = {}
    enrollment_counts = {}
    
   
    trainer_courses = {}
    trainer_enrollments = {}

    for trainer in trainers:
        
        courses = CourseDetails.objects.filter(tenant=tenant, user=trainer.trainer_name).prefetch_related('asanas_by_trainer')
        print(courses,"line no 1128")
        course_counts[trainer.trainer_name.id] = courses.count()
        trainer_courses[trainer.trainer_name.id] = courses 

        
        enrollments = EnrollmentDetails.objects.filter(tenant=tenant, created_by=trainer.trainer_name).select_related('user')
        enrollment_counts[trainer.trainer_name.id] = enrollments.count()
        trainer_enrollments[trainer.trainer_name.id] = enrollments  

    return render(request, 'users/trainers.html', {
        'trainers': trainers,
        'course_counts': course_counts,
        'enrollment_counts': enrollment_counts,
        'trainer_courses': trainer_courses,
        'trainer_enrollments': trainer_enrollments,
        'tenant': tenant,
    })





@login_required
def delete_trainer(request, trainer_id,slug):
    tenant=Tenant.objects.get(slug=slug)
    trainer = get_object_or_404(TrainerLogDetail, id=trainer_id,tenant=tenant)
    CourseDetails.objects.filter(tenant=tenant, user=trainer.trainer_name).delete()
    
    
    EnrollmentDetails.objects.filter(tenant=tenant, created_by=trainer.trainer_name).delete()
    
    trainer.delete()
   
    return redirect('trainer_dashboard',slug=tenant)





@login_required
def edit_trainer(request, trainer_id,slug):
    user = get_object_or_404(User, id=trainer_id)
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
   

@login_required
def  student_dashboard(request, slug):
    tenant = get_object_or_404(Tenant, client_name=request.user, slug=slug)

    
    enrollments = EnrollmentDetails.objects.filter(tenant=tenant).prefetch_related('students_added_to_courses', 'students_added_to_courses__asanas_by_trainer')
    print(enrollments,"skdjfffffffffffffffffff")


    student_enrollment_map = {}
    for enrollment in enrollments:
        if enrollment.user not in student_enrollment_map:
            student_enrollment_map[enrollment.user] = []
        student_enrollment_map[enrollment.user].append(enrollment)
        print(student_enrollment_map,"oooooooooooooooooooooooo")

    context = {
        'tenant': tenant,
        'student_enrollment_map': student_enrollment_map,
    }
    print(student_enrollment_map,"oooooooooooooooooo")
    return render(request, 'users/students.html', context)



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
    user = get_object_or_404(User, id=user_id)
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





@login_required
def register_organisation(request):
    if request.method == 'POST':
        form = OrganisationForm(request.POST,user=request.user)
        if form.is_valid():
            form.save()  
            print("Form is valid. Redirecting to login.")
            return redirect("home")
        else:
            print("Form is invalid. Errors:", form.errors)
    else:
        form = OrganisationForm(user=request.user)

    return render(request, 'users/register_organization.html', {'form': form})




# def tenant_data(request,slug):
#     tenant = getattr(request, 'tenant', None)
#     if tenant:
#         tenant = Tenant.objects.get(slug=slug)
#         asanas=Asana.objects.get(tenant=tenant)
#         subscriptions = EnrollmentDetails.objects.filter(tenant=tenant)
#         other_models = CourseDetails.objects.filter(tenant=tenant)

#         data = (f"Tenants: {tenant.client_name}\n"
#                 f"Asanas: {asanas.name}\n"
#                 f"Subscriptions: {subscriptions.count()}\n"
#                 f"Other Models: {other_models.count()}")

#         return HttpResponse(data)
#     return HttpResponse("Tenant not found")





  #  i need to fetch the user name
        # i need to filter in user objects
        # i need to check the exsiting user
        # if he is trainer or student need to check added_by
        #  from that value i need to check existing url with db url in tenant because tenant is for client 
        #  if he is client that need to directly check with tenant model in url 

















def client_dashboard(request, slug):
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




def tenant_not_found(request):
    return render(request,"users/tenant_not_found.html")





def send_mail_page(request):
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
                )
                context['result'] = 'Email sent successfully'
            except Exception as e:
                context['result'] = f'Error sending email: {e}'
        else:
            context['result'] = 'All fields are required'

    return render(request, "home_page.html", context)


def home_slug(request, slug):
    if slug:
        tenant = get_object_or_404(Tenant, slug=slug)
        print(tenant,"line 1397")
        # Fetch subscriptions if tenant exists
        subscriptions =Tenant.objects.filter(slug=tenant)
        return render(request, "users/home.html", {'subscriptions': subscriptions, 'tenant': tenant})
    else:
        # Render the normal home page if no slug is provided or tenant does not exist
        return render(request, "users/home.html")











def organization_list_view(request):
    organizations = Tenant.objects.all()
    return render(request, 'users/organization_list.html', {'organizations': organizations})

def asanas_view(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    asanas = Asana.objects.filter(tenant=tenant)
    return render(request, 'users/asanas_list.html', {'asanas': asanas, 'tenant': tenant})

def remove_asana_view(request, asana_id):
    asana = get_object_or_404(Asana, id=asana_id)

    if request.method == 'POST':
        asana.delete()  # Deleting the asana
        print("success")
        return redirect('organization_list')  # Redirect back to organization list or another relevant page

    return render(request, 'users/confirm_remove_asana.html', {'asana': asana})

def send_email_view(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    if request.method == 'POST':
        subject = 'Query from Admin'
        message = request.POST.get('message')
        recipient = [tenant.organization_email]
        send_mail(subject, message, 'prabhaprasath07@gmail.com', recipient)
        return redirect('organization_list')
    return render(request, 'users/send_email.html', {'tenant': tenant})

def create_coupon_view(request, tenant_id):
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
            recipient_list=[tenant.organization_email],
        )
        print("send success")
        return redirect('organization_list')

    return render(request, 'users/create_coupon.html', {'tenant': tenant, 'subscriptions': subscriptions})

