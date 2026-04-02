



from celery import shared_task
from django.utils.timezone import now
import logging
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.http import HttpResponse
import time
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded, Retry
from reportlab.pdfgen import canvas
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from celery.signals import task_failure
from django.core.cache import cache
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from random import randint

from django.db import transaction
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
import pandas as pd
from .models import *
from django.core.files.storage import default_storage
from django.utils import timezone
from django.db.models import F
from django.core.mail import send_mail
from django.conf import settings
logger = logging.getLogger('celery_task')

@shared_task
def process_excel_file(file_path, admin_user_id, no_of_persons_onboard_by_client_trainers, no_of_persons_onboard_by_students, tenant_id):
    print(admin_user_id, "hello admin")
    admin_user = User.objects.get(id=admin_user_id)
    get_admin_email=admin_user.email
    tenant = Tenant.objects.get(id=tenant_id)
  
   

    try:
        file_full_path = default_storage.path(file_path)

       
        if no_of_persons_onboard_by_client_trainers > 0 :
            
           
            df_trainers = pd.read_excel(file_full_path, nrows=no_of_persons_onboard_by_client_trainers, engine='openpyxl')
            print(df_trainers,"line 56")
            print(type(df_trainers),"lineeee 58")
            filtered_rows = []
            for index, row in df_trainers.iterrows():
                     role = row['roles'].strip().lower() if isinstance(row['roles'], str) else ""
                     if role == 'trainer':
                          filtered_rows.append(row)
                     else:
                          print(f"Skipping row {index}: Role is not 'Trainer'")
            df_filtered_trainers = pd.DataFrame(filtered_rows)
          
            process_users(df_filtered_trainers, admin_user_id, tenant)

       
        if no_of_persons_onboard_by_students > 0:
           
            df_students = pd.read_excel(file_full_path, skiprows=range(1, no_of_persons_onboard_by_client_trainers + 1), nrows=no_of_persons_onboard_by_students, engine='openpyxl')
            print(df_students,"line 64")
            print(type(df_students),"line 73")
            filtered_rows = []
            for index, row in df_students.iterrows():
                 role = row['roles'].strip().lower() if isinstance(row['roles'], str) else ""
                 if role == 'student':
                       filtered_rows.append(row)
                 else:
                      print(f"Skipping row {index}: Role is not 'Trainer'")
            df_filtered_students = pd.DataFrame(filtered_rows)
          
            process_users(df_filtered_students, admin_user_id, tenant)

        # Cleanup the uploaded file
        default_storage.delete(file_path)
        return "Users onboarded successfully."

    except Exception as e:
        logger.exception("Error processing file: %s", e)
        ErrorHandelingInUserUpload.objects.create(
            tenant=tenant,
            celery_msg=f"Error processing file: {e}",
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_error=True,
        )
        # send_email_task.delay(subject="Error in processing file", message=f"Error processing file: {e}", recipient_list=get_admin_email,from_email="kanii06sshka@gmail.com")
        return f"Error processing file: {e}"


def process_users(df, admin_user_id, tenant):
 try:
 
    user_objs = []
    role_dict = {}
    count_trainer = 0
    count_student = 0

    # Prepare users for bulk creation
    with transaction.atomic():
        for _, row in df.iterrows():
            username = row['username']
            email = row['email']
            first_name = row['first_name']
            last_name = row['last_name']
            role=row['roles']
           
            if User.objects.filter(username=username).exists():
                    print(f"Username {username} already exists. Skipping.")
                    continue

            if User.objects.filter(email=email).exists():
                    print(f"Email {email} already exists. Skipping.")
                    continue

            user_details = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
               
            )
            user_objs.append(user_details)
            role_dict[username] = role
        
        # Bulk create users
        User.objects.bulk_create(user_objs)
        print(f"{role.capitalize()}s created")
       
        # Assign roles and onboard users
        admin_user = User.objects.get(id=admin_user_id)
        get_admin_email=admin_user.email
        client_onboarding, _ = ClientOnboarding.objects.get_or_create(client=admin_user, tenant=tenant)
        print("client onboarding is createed ",client_onboarding)

        for user in user_objs:
            print("usrr enterend for loop")
            role = role_dict[user.username]

            group, _ = Group.objects.get_or_create(name=role.capitalize())
           
            user.groups.add(group)
           

            if role.lower() == 'trainer' :
             
                count_trainer = onboard_trainer(user, admin_user, tenant, count_trainer)
               
               
               
            elif role.lower()== 'student':
               
               
                count_student = onboard_student(user, admin_user, tenant, count_student)
               
                
        if count_trainer > 0 or count_student >0:
             client_onboarding.trainers_onboarded = F('trainers_onboarded') + count_trainer
             client_onboarding.students_onboarded = F('students_onboarded') + count_student
             client_onboarding.save()


        ErrorHandelingInUserUpload.objects.create(
                tenant=tenant,
                celery_msg=f"Updated trainers: {client_onboarding.trainers_onboarded}, students: {client_onboarding.students_onboarded}",
                created_at=timezone.now(),
                updated_at=timezone.now(),
                is_error=False,
            )
        
              

       
   
           

        print(f"Updated trainers: {client_onboarding.trainers_onboarded}, students: {client_onboarding.students_onboarded}")
 except Exception as e:
    logger.exception("process_users failed: %s", e)
     
 
           


def onboard_trainer(user, admin_user, tenant, count_trainer):
 print("enternd to create trainer model")
 admin_user = User.objects.get(username=admin_user)
 get_admin_email=admin_user.email
 try:
    TrainerLogDetail.objects.create(
        trainer_name=user,
        onboarded_by=admin_user,
        tenant=tenant,
        no_of_asanas_created=0,
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )
    count_trainer += 1
    print(count_trainer,"llllllllllllllllllllllllll")
    # send_welcome_email(user, admin_user, role='Trainer')
    print(f"Trainer onboarded. Total trainers: {count_trainer}")
    return count_trainer
 except Exception as e:
    logger.exception("onboard_trainer failed: %s", e)



def onboard_student(user, admin_user, tenant, count_student):
    print("enternd to create trainer model")
    admin_user = User.objects.get(username=admin_user)

    try:
         
        if admin_user:
            


            StudentLogDetail.objects.create(
                student_name=user,
                added_by=admin_user,
                mentor=None,
                tenant=tenant,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
            count_student += 1
            print(count_student, "ggggggggggh")
            # send_welcome_email(user, admin_user, role='Student')
            print(f"Student onboarded. Total students: {count_student}")
        return count_student
    except Exception as e:
        logger.exception("onboard_student failed: %s", e)

def send_welcome_email(user, admin_user, role):
    get_admin_user=User.objects.get(username=admin_user)
    get_admin_email=get_admin_user.email
    get_user=User.objects.get(username=user)
    get_user_email=get_user.email

    default_password = User.objects.make_random_password()
    user.set_password(default_password)
    user.save()
    subject = f"Welcome to Our Platform Knowinmy!"
    message = (
        f"Hi {user.username},\n"
        f"Welcome to Knowinmy! You have been onboarded to the platform as a {role}. Your default password is: {default_password}\n\n"
        f"Please reset your password as soon as possible.\n\n"
        f"Best regards,\nKnowinmy Team"
    )
    from_email = get_admin_email
    recipient_list =get_user_email
    print(recipient_list,"lineeee")
    send_email_task.delay(subject, message,  recipient_list,from_email)





@shared_task
def send_payment_invoice_task(order_id):
    """Generate PDF invoice and email it to the user."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from io import BytesIO
    from django.core.mail import EmailMessage
    from django.template.loader import render_to_string

    try:
        order = Order.objects.select_related('user').get(id=order_id)
        user = order.user
        if not user:
            return

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 20)
        p.setFont("Helvetica", 12)
        p.drawString(100, 800, "Knowinmy")
        p.line(50, 770, 550, 770)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 750, "Payment Details")
        p.setFont("Helvetica", 12)
        p.drawString(100, 720, f"Name: {order.name}")
        p.drawString(100, 700, f"Amount: {order.amount}")
        p.drawString(100, 680, f"Payment ID: {order.payment_id}")
        p.line(50, 660, 550, 660)
        p.setFont("Helvetica", 10)
        p.drawString(50, 40, "Thank you for choosing Knowinmy!")
        p.drawString(50, 25, "For inquiries, contact us at support@knowinmy.com or visit www.knowinmy.com")
        p.showPage()
        p.save()

        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()

        email_subject = f"Payment Invoice for Order {order.provider_order_id}"
        email_body = render_to_string('users/payment_invoice.html', {
            'order': order,
            'user': user,
        })

        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach('payment_invoice.pdf', pdf_data, 'application/pdf')
        email.send()
    except Exception as e:
        logger.exception("send_payment_invoice_task failed: %s", e)


@shared_task(time_limit=10,bind=True,max_retries=2)
def send_email_task(self,subject, message, recipient_list, from_email=None):
    """Asynchronous email sending function with a time limit."""
    try:
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL  

        # Ensure recipient_list is a flat list
        print(from_email,"lineutturgiigr")
        print(recipient_list,"line kfmklfmgbkmlk   gggg")
        
        
        if isinstance(recipient_list, str):
            recipient_list = [recipient_list]
        elif isinstance(recipient_list, list) and len(recipient_list) > 0 and isinstance(recipient_list[0], list):
            recipient_list = recipient_list[0]  # Flatten nested list
            print(recipient_list,"line    gggg")

        # Validate and send emails
        # valid_emails = []
        # for email in recipient_list:
        #     try:
        #         validate_email(email)  # Validate email format
        #         valid_emails.append(email)
        #     except ValidationError:
        #         print(f"Invalid email address: {email}")
        #         continue

        # if not valid_emails:
        #     print("No valid email addresses to send to.")
        #     return

        # Send the email
        print(from_email,"line")
        print(recipient_list,"line    gggg")

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        print(f"Email sent to: {', '.join(recipient_list)}")

    except SoftTimeLimitExceeded:
        print("Task exceeded the time limit and was terminated.")
        # Perform any necessary cleanup here
        print("Task exceeded the time limit and was terminated. Rescheduling...")
        try:
            # Retry the task with a delay of 10 seconds
            raise self.retry(countdown=10, exc=SoftTimeLimitExceeded())
        except Retry:
            print("Max retries exceeded for task.")




@shared_task
def notify_users_for_renew():
    get_orders=Order.objects.all()
    for orders in get_orders:
        if orders.subscription.end_date<= now():
            if not orders.user:
                continue
            get_email=orders.user.email
            send_email_task.delay(subject="Regarding Renewl of subscription",message="Your subscription got expired kindly renew it by pay the plan again",from_email=settings.EMAIL_HOST_USER,recipient_list=get_email)
            orders.is_active = False
            orders.save()


@shared_task
def send_welcome_mail_for_user(admin_user_id, tenant_id):
    """
    Send welcome emails to students and trainers of a tenant and set default passwords.
    """
    admin_user = User.objects.filter(id=admin_user_id).first()
    tenant = Tenant.objects.filter(id=tenant_id).first()

    if not admin_user or not tenant:
        return  # Handle missing data gracefully

    admin_email = settings.EMAIL_HOST_USER

    # Fetch students and trainers for the tenant
    students = StudentLogDetail.objects.filter(tenant=tenant)
    trainers = TrainerLogDetail.objects.filter(tenant=tenant)

    # Send emails to students
    for student in students:
        user = User.objects.filter(username=student.student_name).first()
        if user:
            default_password = User.objects.make_random_password()
            user.set_password(default_password)
            user.save()
            

            send_mail(
                subject="Welcome to Our Platform Knowinmy!",
                message=(
                    f"Hi {student.student_name},\n\n"
                    f"Welcome to Knowinmy! You have been onboarded to the platform as a student. "
                    f"Your default password is: {default_password}\n\n"
                    f"Please reset your password as soon as possible.\n\n"
                    f"Best regards,\nKnowinmy Team"
                ),
                recipient_list=[user.email],
                from_email=admin_email
            )

    # Send emails to trainers
    for trainer in trainers:
        user = User.objects.filter(username=trainer.trainer_name).first()
        if user:
            default_password = User.objects.make_random_password()
            user.set_password(default_password)
            user.save()
            send_mail(
                subject="Welcome to Our Platform Knowinmy!",
                message=(
                    f"Hi {trainer.trainer_name},\n\n"
                    f"Welcome to Knowinmy! You have been onboarded to the platform as a trainer. "
                    f"Your default password is: {default_password}\n\n"
                    f"Please reset your password as soon as possible.\n\n"
                    f"Best regards,\nKnowinmy Team"
                ),
                recipient_list=[user.email],
                from_email=admin_email
            )
@shared_task
def send_scheduled_email(subject, message, recipient_list, from_email):
    print(from_email,recipient_list,"linebhjhjhj")
    send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    print(f"Email sent to {recipient_list} with subject: {subject}")



@shared_task
def renew_subscription_task():
   
    users = User.objects.filter(is_active=True)
    for user in users:
        print(user.username, "Checking user subscriptions")
        get_order = Order.objects.filter(user=user, is_active=True)
        if get_order:
            for orders in get_order:
                print(orders, "Processing order")
                if orders.is_active:
                    subscription_end = orders.subscription.end_date
                    subscription_start = orders.subscription.start_date
                    get_day_to_send_email = (subscription_end - subscription_start).days / 2
                    future_time_notify_email = timezone.now() + timedelta(days=get_day_to_send_email)
                    
                    print(future_time_notify_email, "Notification email time")
                    if future_time_notify_email:
                        print("emaillll send ")
                        send_scheduled_email.apply_async(
                            args=[
                                "Notification about renewal",
                                "Your subscription is about to expire soon. Kindly renew it to continue using our services.",
                                [user.email],
                                settings.EMAIL_HOST_USER
                            ],
                            eta=future_time_notify_email
                        )

                    
                   
                    if orders.subscription.end_date <= timezone.now():
                        print(f"Subscription ended for order {orders.id}")
                        send_mail(
                            subject="Regarding Renewl of subscription",
                            message="Your subscription got expired kindly renew it by pay the plan again",  
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[user.email])
                        orders.is_active = False
                        orders.save()
                    
                    
                    if not orders.is_active and orders.subscription.end_date >= timezone.now():
                        print(f"Reactivating subscription for order {orders.id}")
                        orders.is_active = True
                        orders.save()
                        send_mail(  
                            subject="Subscription Renewed",
                            message="Your subscription has been renewed successfully",
                            from_email=settings.EMAIL_HOST_USER,  
                            recipient_list=[user.email])
        else:
            print(f"No active orders found for user {user.username}")