from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.urls import path
from .views import CreateAsanaView





urlpatterns = [
    # Base path with slug
    path('', home, name='home'),
    path('home/<slug:slug>/',home_slug,name="home-slug"),
    path('send-mail/', send_mail_page, name='send_mail_page'),
    path('register/', register, name='register'),
    path('register-organisation/', register_organisation, name='register_organization'),
    path('subscription_plans/',subscription_plans,name='subscriptions_plans'),
    path('login/', user_login, name='login'),
    path('dashboard/', role_based_dashboard, name='role_based_dashboard'),
    path('renew/',renew_subscription,name='renew'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset_form.html', ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',form_class=CustomSetPasswordForm), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
    path('payment/', subscription_payment, name='subscription-payment'),
    path('razorpay/callback/', callback, name='callback'),
    path('<slug:slug>/logout/', log_out, name='log_out'),
    path('logout/', log_out, name='log_out'),
    # see with the path of log_out name in url 
    path('<slug:slug>/create_asana/', CreateAsanaView.as_view(), name='create-asana'),
    path('<slug:slug>/update_asana/<int:asana_id>/', CreateAsanaView.as_view(), name='update_asana'),
    path('<slug:slug>/staff_dashboard/', staff_dashboard_function, name='staff_dashboard'),
    path('<slug:slug>/view_trained/', view_trained, name='view-trained'),
    path('<slug:slug>/view_posture/<int:asana_id>/', view_posture, name='view-posture'),
    path('<slug:slug>/edit_postures/<int:posture_id>/', edit_posture, name='edit-posture'),
    path('<slug:slug>/user_view_asana/', user_view_asana, name='user-view-asana'),
    path('<slug:slug>/user_view_posture/<int:asana_id>/', user_view_posture, name='user-view-posture'),
    path('<slug:slug>/get_posture/<int:posture_id>/', get_posture, name='get-posture'),
    path('<slug:slug>/trainer_approval/', Trainer_approval_function, name='Trainer-approval'),
    path('<slug:slug>/onboarding_users_form/', onboarding_view, name='onboard-users-form'),
    path('<slug:slug>/client_table/', client_list, name='client-list'),
    path('<slug:slug>/trainer_dashboard/',CourseCreationView.as_view(), name='create-course'),
    path('<slug:slug>/update_course/<int:course_id>/', CourseCreationView.as_view(), name='update_course'),
    path('<slug:slug>/profile/', profile_view, name='profile-user'),
    path('<slug:slug>/update_profile/', update_profile, name='update_profile'),
    path('<slug:slug>/show_subs/', get_subscription_details_for_client, name='get-subs-for-client'),

    path('<slug:slug>/student_mapping/', StudentCourseMapView.as_view(), name='student-mapp-courses'),
    path('<slug:slug>/update_student_course/<int:enrollment_id>/', StudentCourseMapView.as_view(), name='student-course-update'),
    path('<slug:slug>/clients/', client_list, name='client_list'),
  
    path('<slug:slug>/get_posture_dataset/', get_posture_dataset, name='get-posture-dataset'),
    path('<slug:slug>/client_dashboard/', client_dashboard, name='client_dashboard'),
    path('tenant_not_found/',tenant_not_found,name=" "),
    
    path('<slug:slug>/trainers/', trainer_dashboard, name='trainer_dashboard'),
   
    path('trainer/edit/<int:user_id>/<slug:slug>/', edit_trainer, name='edit_trainer'),
    path('<slug:slug>/trainer/delete/<int:trainer_id>/', delete_trainer, name='delete_trainer'),
     path('<slug:slug>/edit_user/<int:user_id>/', edit_user, name='edit_user'),
    path('<slug:slug>/students/', student_dashboard, name='student_dashboard'),
    path('<slug:slug>/students/delete/<int:student_id>/', delete_student, name='delete_student'),
    path('organizations/', organization_list_view, name='organization_list'),
    path('organizations/<int:tenant_id>/asanas/', asanas_view, name='asanas_view'),
    
    path('organizations/<int:tenant_id>/send-email/', send_email_view, name='send_email_view'),
    path('asanas/<int:asana_id>/remove/', remove_asana_view, name='remove_asana_view'),
    path('organizations/<int:tenant_id>/create-coupon/', create_coupon_view, name='create_coupon_view'),
    path('<slug:slug>/students_to_trainers/', student_dashboard_for_trainer, name='student_dashboard_trainer'),
    path('<slug:slug>/enable_disable_user/<int:user_id>/',enable_or_disable_user,name='toggle_permission'),
    path('subscribe/',dynamic_subscription_payment,name='dynamic'),
    path('request-slug-change/', request_slug_change, name='request_slug_change'),
    path('review-slug-changes/', review_slug_changes, name='review_slug_changes'),
    path('<slug:slug/request_subscription_change/', subscription_change_request, name='subscription_change_request'),
    path('subscription-requests/', list_subscription_requests, name='list_subscription_requests'),
    path('approve_subscription_change/<int:request_id>/', approve_subscription_change_by_knowinmy, name='approve_subscription_change'),
    path('request-subscription-change/', subscription_change_request, name='subscription_change_request'),
   
   
    # Add other URLs as needed


    # Define a URL for tenant-specific data
    # path('<slug:slug>/tenant-data/', tenant_data, name='tenant-data'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    