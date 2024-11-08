from celery import shared_task
from django.db import transaction
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
import pandas as pd
from .models import *
from django.core.files.storage import default_storage
from django.utils import timezone
from django.db.models import F

@shared_task
def process_excel_file(file_path, admin_user_id, no_of_persons_onboard_by_client, tenant_id):
    tenant = Tenant.objects.get(id=tenant_id)
    print("Processing Excel file with the following parameters:", no_of_persons_onboard_by_client, admin_user_id, tenant_id)

    try:
        # Load the file
        file_full_path = default_storage.path(file_path)
        df = pd.read_excel(file_full_path, nrows=no_of_persons_onboard_by_client, engine='openpyxl')
        print("DataFrame loaded")

        user_objs = []
        role_dict = {}
        
        with transaction.atomic():
            for i, row in df.iterrows():
                username = row['username']
                email = row['email']
                first_name = row['first_name']
                last_name = row['last_name']
                mentor_email = row['mentor'] if row['mentor'] != 'none' else None
                role = row['roles'].lower()

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
            print("Users created")

            # Fetch admin_user instance
            admin_user = User.objects.get(id=admin_user_id)
            
            # Fetch or create ClientOnboarding record for admin_user
            client_onboarding, created = ClientOnboarding.objects.get_or_create(
                client=admin_user, tenant=tenant)

            if client_onboarding:
                for user in user_objs:
                    role = role_dict[user.username]
                    group, _ = Group.objects.get_or_create(name=role.capitalize())
                    user.groups.add(group)
                    
                    if role == 'trainer' and not mentor_email:
                        # Handle trainer without mentor
                        TrainerLogDetail.objects.create(
                            trainer_name=user,
                            onboarded_by=admin_user,
                            tenant=tenant,
                            no_of_asanas_created=0, 
                            created_at=timezone.now(),
                            updated_at=timezone.now(),
                        )
                        client_onboarding.trainers_onboarded = F('trainers_onboarded') + 1
                    elif role == 'student' and mentor_email:
                        try:
                            # Fetch mentor from User
                            mentor_user = get_object_or_404(User, email=mentor_email)
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
                            client_onboarding.students_onboarded = F('students_onboarded') + 1
                        except User.DoesNotExist:
                            print(f"No User found with email {mentor_email}. Skipping student {user.username}.")
                            continue  # Skip this student if mentor not found
                        except TrainerLogDetail.DoesNotExist:
                            print(f"No TrainerLogDetail found for mentor with email {mentor_email}. Skipping student {user.username}.")
                            continue  # Skip this student if mentor details not found

                client_onboarding.save()  # Save the updated counts to the database
            else:
                print("ClientOnboarding not found.")

        # Cleanup the uploaded file
        default_storage.delete(file_path)
        return "Users onboarded successfully."

    except Exception as e:
        print(f"Error processing file: {e}")
        return f"Error processing file: {e}"
