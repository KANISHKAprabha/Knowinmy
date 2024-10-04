# from django.test import TestCase
# from django.contrib.auth.models import User
# from django.utils import timezone
# from users.models import Tenant, Asana, Posture, CourseDetails, EnrollmentDetails, Subscription, Order, TrainerLogDetail, StudentLogDetail, ClientOnboarding,CouponCodeForNegeotiation

# class TenantFormTests(TestCase):

#     def setUp(self):
#         # Create a user for testing
#         self.user = User.objects.create(username="testuser", email="testuser@example.com", password="password123")

#     def test_tenant_creation(self):
#         """Test if tenant is created successfully"""
#         tenant = Tenant.objects.create(
#             client_name=self.user,
#             organization_name="Test Organization",
#             domain_name="testorganization-com",
#             organization_email="info@testorganization-com"
#         )
#         self.assertEqual(tenant.slug, "testorganization-com")
#         self.assertEqual(tenant.organization_name, "Test Organization")
#         self.assertEqual(tenant.full_url, f"http://127.0.0.1:8000/.{tenant.slug}.com")

#     def test_slug_generation_on_save(self):
#         """Test if slug and full_url are generated properly on saving"""
#         tenant = Tenant.objects.create(
#             client_name=self.user,
#             organization_name="New Org",
#             domain_name="neworg_com",
#             organization_email="contact@neworg.com"
#         )
#         tenant.save()
#         self.assertEqual(tenant.slug, "neworg_com")
#         self.assertIn("neworgcom.com", tenant.full_url)


# class AsanaFormTests(TestCase):

#     def setUp(self):
#         self.user = User.objects.create(username="asanauser", email="asanauser@example.com", password="password123")
#         self.tenant = Tenant.objects.create(
#             client_name=self.user,
#             organization_name="Yoga Org",
#             domain_name="yogaorg.com",
#             organization_email="info@yogaorg.com"
#         )

#     def test_asana_creation(self):
#         """Test the creation of an Asana instance"""
#         asana = Asana.objects.create(
#             name="Test Asana",
#             no_of_postures=5,
#             created_by=self.user,
#             tenant=self.tenant,
#             created_at=timezone.now(),
#             last_modified_at=timezone.now(),
#             is_active=True
#         )
#         self.assertEqual(asana.name, "Test Asana")
#         self.assertEqual(asana.no_of_postures, 5)
#         self.assertEqual(asana.tenant, self.tenant)

#     def test_asana_str_representation(self):
#         """Test the string representation of Asana"""
#         asana = Asana.objects.create(
#             name="Mountain Pose",
#             no_of_postures=3,
#             created_by=self.user,
#             tenant=self.tenant,
#             created_at=timezone.now(),
#             last_modified_at=timezone.now()
#         )
#         self.assertEqual(str(asana), "Mountain Pose")


# class PostureFormTests(TestCase):

#     def setUp(self):
#         self.user = User.objects.create(username="postureuser", email="postureuser@example.com", password="password123")
#         self.tenant = Tenant.objects.create(
#             client_name=self.user,
#             organization_name="Posture Org",
#             domain_name="postureorg.com",
#             organization_email="info@postureorg.com"
#         )
#         self.asana = Asana.objects.create(
#             name="Test Asana",
#             no_of_postures=5,
#             created_by=self.user,
#             tenant=self.tenant,
#             created_at=timezone.now(),
#             last_modified_at=timezone.now(),
#             is_active=True
#         )

#     def test_posture_creation(self):
#         """Test the creation of a Posture instance"""
#         posture = Posture.objects.create(
#             tenant=self.tenant,
#             step_no=1,
#             name="Posture 1",
#             asana=self.asana,
#             snap_shot=None,
#             last_modified_at=timezone.now(),
#             first_trained_at=timezone.now(),
#             is_active=True
#         )
#         self.assertEqual(posture.name, "Posture 1")
#         self.assertEqual(posture.asana, self.asana)
#         self.assertEqual(posture.tenant, self.tenant)

#     def test_posture_str_representation(self):
#         """Test the string representation of Posture"""
#         posture = Posture.objects.create(
#             tenant=self.tenant,
#             step_no=2,
#             name="Warrior Pose",
#             asana=self.asana,
#             snap_shot=None,
#             last_modified_at=timezone.now(),
#             first_trained_at=timezone.now()
#         )
#         self.assertEqual(str(posture), "Warrior Pose")


# class SubscriptionFormTests(TestCase):

#     def setUp(self):
#         self.user = User.objects.create(username="subuser", email="subuser@example.com", password="password123")
#         self.tenant = Tenant.objects.create(
#             client_name=self.user,
#             organization_name="Subscription Org",
#             domain_name="suborg.com",
#             organization_email="info@suborg.com"
#         )

#     def test_subscription_creation(self):
#         """Test if a Subscription is created successfully"""
#         subscription = Subscription.objects.create(
#             tenant=self.tenant,
#             name="Yoga Subscription",
#             description="Access to all Yoga classes",
#             permitted_asanas=50,
#             no_of_persons_onboard=10,
#             price=299.99,
#             highlight_status=False,
#             created_at=timezone.now(),
#             updated_at=timezone.now()
#         )
#         self.assertEqual(subscription.name, "Yoga Subscription")
#         self.assertEqual(subscription.price, 299.99)
#         self.assertEqual(subscription.permitted_asanas, 50)



# class TenantModelTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='password')
#         self.tenant = Tenant.objects.create(
#             client_name=self.user,
#             organization_name="Test Organization",
#             domain_name="testorganization_com",
#             organization_email="test@example.com"
#         )

#     def test_tenant_creation(self):
#         self.assertIsInstance(self.tenant, Tenant)

#     def test_slug_generation_on_save(self):
#         self.assertEqual(self.tenant.slug, "testorganization_com")

#     def test_full_url(self):
#         self.assertEqual(self.tenant.full_url, "http://127.0.0.1:8000/.testorganization_com.com")


# class AsanaModelTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='password')
#         self.tenant = Tenant.objects.create(client_name=self.user, organization_name="Test Org", domain_name="test.org", organization_email="test@test.com")
#         self.asana = Asana.objects.create(
#             name="Warrior Pose",
#             no_of_postures=1,
#             created_by=self.user,
#             tenant=self.tenant,
#             created_at="2023-09-20",
#             last_modified_at="2023-09-20"
#         )

#     def test_asana_creation(self):
#         self.assertIsInstance(self.asana, Asana)

#     def test_asana_str_representation(self):
#         self.assertEqual(str(self.asana), "Warrior Pose")


# class PostureModelTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='password')
#         self.tenant = Tenant.objects.create(client_name=self.user, organization_name="Test Org", domain_name="test.org", organization_email="test@test.com")
#         self.asana = Asana.objects.create(
#             name="Warrior Pose",
#             no_of_postures=1,
#             created_by=self.user,
#             tenant=self.tenant,
#             created_at="2023-09-20",
#             last_modified_at="2023-09-20",
#             is_active=True
#         )
#         self.posture = Posture.objects.create(
#             tenant=self.tenant,
#             step_no=1,
#             name="Warrior Pose Step",
#             asana=self.asana,
#             first_trained_at="2023-09-20",
#             last_modified_at="2023-09-20",
#             is_active=True
#         )

#     def test_posture_creation(self):
#         self.assertIsInstance(self.posture, Posture)

#     def test_posture_str_representation(self):
#         self.assertEqual(str(self.posture), "Warrior Pose Step")


# class CourseDetailsModelTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='password')
#         self.tenant = Tenant.objects.create(client_name=self.user, organization_name="Test Org", domain_name="test.org", organization_email="test@test.com")
#         self.course = CourseDetails.objects.create(
#             tenant=self.tenant,
#             course_name="Yoga Basics",
#             description="An introductory course on Yoga",
#             user=self.user,
#             created_at="2023-09-20",
#             updated_at="2023-09-20"
#         )

#     def test_course_creation(self):
#         self.assertIsInstance(self.course, CourseDetails)

#     def test_course_str_representation(self):
#         self.assertEqual(str(self.course), "Yoga Basics")


# class EnrollmentDetailsModelTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='password')
#         self.tenant = Tenant.objects.create(client_name=self.user, organization_name="Test Org", domain_name="test.org", organization_email="test@test.com")
#         self.course = CourseDetails.objects.create(
#             tenant=self.tenant,
#             course_name="Yoga Basics",
#             description="An introductory course on Yoga",
#             user=self.user,
#             created_at="2023-09-20",
#             updated_at="2023-09-20"
#         )
#         self.enrollment = EnrollmentDetails.objects.create(
#             tenant=self.tenant,
#             user=self.user,
#             created_at="2023-09-20",
#             updated_at="2023-09-20"
#         )

#     def test_enrollment_creation(self):
#         self.assertIsInstance(self.enrollment, EnrollmentDetails)

#     def test_enrollment_str_representation(self):
#         self.assertEqual(str(self.enrollment), self.user.username)


# class SubscriptionModelTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='password')
#         self.tenant = Tenant.objects.create(client_name=self.user, organization_name="Test Org", domain_name="test.org", organization_email="test@test.com")
#         self.subscription = Subscription.objects.create(
#             tenant=self.tenant,
#             name="Basic Subscription",
#             description="Basic plan for users",
#             permitted_asanas=10,
#             no_of_persons_onboard=5,
#             price=99.99,
#             created_at="2023-09-20",
#             updated_at="2023-09-20"
#         )

#     def test_subscription_creation(self):
#         self.assertIsInstance(self.subscription, Subscription)

#     def test_subscription_str_representation(self):
#         self.assertEqual(str(self.subscription.name), "Basic Subscription")


# class OrderModelTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='password')
#         self.tenant = Tenant.objects.create(client_name=self.user, organization_name="Test Org", domain_name="test.org", organization_email="test@test.com")
#         self.subscription = Subscription.objects.create(
#             tenant=self.tenant,
#             name="Basic Subscription",
#             description="Basic plan for users",
#             permitted_asanas=10,
#             no_of_persons_onboard=5,
#             price=99.99,
#             created_at="2023-09-20",
#             updated_at="2023-09-20"
#         )
#         self.order = Order.objects.create(
#             tenant=self.tenant,
#             subscription=self.subscription,
#             name="Test Customer",
#             amount=99.99,
#             status='PENDING',
#             provider_order_id='ORDER123',
#             payment_id='PAYMENT123',
#             signature_id='SIGNATURE123',
#             created_at="2023-09-20",
#             updated_at="2023-09-20"
#         )

#     def test_order_creation(self):
#         self.assertIsInstance(self.order, Order)

#     def test_order_str_representation(self):
#         self.assertEqual(str(self.order), f"{self.order.id}-{self.order.name}-{self.order.status}")


# class CouponCodeForNegotiationModelTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='password')
#         self.tenant = Tenant.objects.create(client_name=self.user, organization_name="Test Org", domain_name="test.org", organization_email="test@test.com")
#         self.subscription = Subscription.objects.create(
#             tenant=self.tenant,
#             name="Basic Subscription",
#             description="Basic plan for users",
#             permitted_asanas=10,
#             no_of_persons_onboard=5,
#             price=99.99,
#             created_at="2023-09-20",
#             updated_at="2023-09-20"
#         )
#         self.coupon = CouponCodeForNegeotiation.objects.create(
#             tenant=self.tenant,
#             user=self.user,
#             subscription_for_coupon_code=self.subscription,
#             discount_percentage=10,
#             created_at="2023-09-20",
#             updated_at="2023-09-20"
#         )

#     def test_coupon_creation(self):
#         self.assertIsInstance(self.coupon, CouponCodeForNegeotiation)

#     def test_coupon_str_representation(self):
#         self.assertEqual(str(self.coupon), self.coupon.code)


# class TrainerLogDetailModelTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='password')
#         self.tenant = Tenant.objects.create(client_name=self.user, organization_name="Test Org", domain_name="test.org", organization_email="test@test.com")
#         self.trainer_log = TrainerLogDetail.objects.create(
#             tenant=self.tenant,
#             trainer_name=self.user,
#             onboarded_by=self.user,
#             no_of_asanas_created=5,
#             created_at="2023-09-20",
#             updated_at="2023-09-20"
#         )

#     def test_trainer_log_creation(self):
#         self.assertIsInstance(self.trainer_log, TrainerLogDetail)

#     def test_trainer_log_str_representation(self):
#         self.assertEqual(str(self.trainer_log), self.trainer_log.trainer_name.username)


# class StudentLogDetailModelTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='password')
#         self.tenant = Tenant.objects.create(client_name=self.user, organization_name="Test Org", domain_name="test.org", organization_email="test@test.com")
#         self.student_log = StudentLogDetail.objects.create(
#             tenant=self.tenant,
#             student_name=self.user,
#             added_by=self.user,
#             created_at="2023-09-20",
#             updated_at="2023-09-20"
#         )

#     def test_student_log_creation(self):
#         self.assertIsInstance(self.student_log, StudentLogDetail)

#     def test_student_log_str_representation(self):
#         self.assertEqual(str(self.student_log), self.student_log.student_name.username)


# class ClientOnboardingModelTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='password')
#         self.tenant = Tenant.objects.create(client_name=self.user, organization_name="Test Org", domain_name="test.org", organization_email="test@test.com")
#         self.client_onboarding = ClientOnboarding.objects.create(
#             tenant=self.tenant,
#             client=self.user,
#             trainers_onboarded = 5,
#             students_onboarded = 4
            
#         )

#     def test_client_onboarding_creation(self):
#         self.assertIsInstance(self.client_onboarding, ClientOnboarding)

#     def test_client_onboarding_str_representation(self):
#         self.assertEqual(str(self.client_onboarding), self.client_onboarding.client.username)







from unittest.mock import patch
from django.utils import timezone
from django.test import TestCase, RequestFactory
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from users.views import *
from users.models import TrainerLogDetail, StudentLogDetail, Tenant,Asana,Posture

from django.contrib.auth import get_user_model

User = get_user_model()
# class UserLogoutViewTest(TestCase):
#     def setUp(self):
#         self.client_user = User.objects.create_user(username="clientuser", email="client@example.com", password="testpassword")
#         self.trainer_user = User.objects.create_user(username="traineruser", email="trainer@example.com", password="testpassword")
#         self.student_user = User.objects.create_user(username="studentuser", email="student@example.com", password="testpassword")
        
       
#         self.tenant = Tenant.objects.create(client_name=self.client_user, slug="tenant_slug")
#         self.trainer_log = TrainerLogDetail.objects.create(trainer_name=self.trainer_user, tenant=self.tenant)
#         self.student_log = StudentLogDetail.objects.create(student_name=self.student_user, tenant=self.tenant)
    

#     def test_log_out_test(self):
#         url = reverse('home-slug', kwargs={'slug': self.tenant.slug})

#         data = {"email": "client@example.com", "password": "testpassword","tenant":"tenant_slug"}
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, 200)
        
#         self.assertIn('tenant', response.context)


# class UserLoginView(TestCase):
#     def setUp(self):
#         self.client_user = User.objects.create(username="clientuser", email="client@example.com")
#         self.client_user.set_password('testpassword')
#         self.trainer_user = User.objects.create_user(username="traineruser", email="trainer@example.com", password="testpassword")
#         self.student_user = User.objects.create_user(username="studentuser", email="student@example.com", password="testpassword")
        
       
#         self.tenant = Tenant.objects.create(client_name=self.client_user, slug="tenant_slug")
#         self.trainer_log = TrainerLogDetail.objects.create(trainer_name=self.trainer_user, tenant=self.tenant)
#         self.student_log = StudentLogDetail.objects.create(student_name=self.student_user, tenant=self.tenant)
    
        
#     def test_user_login_as_client(self):
#         url= reverse('login')
#         data = {"email": "client@example.com", "password": "testpassword"}
#         response=self.client.post(url,data)
       
             
#         self.assertEqual(response.status_code,302)
#         self.assertTemplateUsed("users/login.html")

#     def test_user_login_as_trainer(self):
#         url= reverse('login')
#         data = {"email": "trainer@example.com", "password": "testpassword"}
#         response=self.client.post(url,data)
       
             
#         self.assertEqual(response.status_code,302)
#         self.assertTemplateUsed("users/login.html")

#     def test_user_login_as_student(self):
#         url= reverse('login')
#         data = {"email": "student@example.com", "password": "testpassword"}
#         response=self.client.post(url,data)
       
             
#         self.assertEqual(response.status_code,302)
#         self.assertTemplateUsed("users/login.html")





# class RoleBasedDashboardTest(TestCase):
#     def setUp(self):
#         self.client_user = User.objects.create(username="clientuser", email="client@example.com")
#         self.client_user.set_password('testpassword')
#         self.client_user.save()
#         self.trainer_user = User.objects.create_user(username="traineruser", email="trainer@example.com", password="testpassword")
#         self.student_user = User.objects.create_user(username="studentuser", email="student@example.com", password="testpassword")
        
#         self.tenant = Tenant.objects.create(client_name=self.client_user, slug="tenant_slug")
#         self.trainer_log = TrainerLogDetail.objects.create(trainer_name=self.trainer_user, tenant=self.tenant)
#         self.student_log = StudentLogDetail.objects.create(student_name=self.student_user, tenant=self.tenant)
    

#     def test_client_dashboard(self):
#         data=self.client.login(username="clientuser", password="testpassword") 
#         self.assertTrue(data)
#         url = reverse('role_based_dashboard')
#         response=self.client.post(url)
#         get_client=User.objects.get(username=self.client_user.username)
#         if get_client:
#             get_tenant_for_client= Tenant.objects.get(client_name=get_client)
#             tenant=get_tenant_for_client.slug
#             self.assertEqual(response.status_code,200)
#             self.assertTemplateUsed("users/Trainer_approval_Page.html")

#     def test_trainer_dashboard(self):
#         data=self.client.login(username="traineruser", password="testpassword")
#         self.assertTrue(data)
#         url = reverse('role_based_dashboard')
#         response=self.client.post(url)
#         get_trainer=User.objects.get(username=self.trainer_user.username)
#         if get_trainer:
#             get_trainer_for_slug=TrainerLogDetail.objects.get(trainer_name=get_trainer)
#             get_slug=get_trainer_for_slug.tenant

#             get_tenant_for_trainer= Tenant.objects.get(slug=get_slug)
#             print(get_tenant_for_trainer)
            
#             self.assertEqual(response.status_code,200)
#             self.assertTemplateUsed("users/view_trained.html")

#     def test_student_dashboard(self):
#         data=self.client.login(username="studentuser", password="testpassword")
#         self.assertTrue(data)
#         url = reverse('role_based_dashboard')
#         response=self.client.post(url)
#         get_student=User.objects.get(username=self.student_user.username)
#         if get_student:
#             get_student_for_slug=StudentLogDetail(student_name=self.student_user.username)
#             get_slug=get_student_for_slug.tenant

#             get_tenant_for_client= Tenant.objects.get(slug=get_slug)
            
#             self.assertEqual(response.status_code,200)
#             self.assertTemplateUsed("users/student_mapping.html")
          



        





# User = get_user_model()

# class ViewTrainedAndPostureTest(TestCase):
#     def setUp(self):
        
#         self.trainer_user = User.objects.create_user(username="traineruser", email="trainer@example.com", password="testpassword")
#         self.student_user = User.objects.create_user(username="studentuser", email="student@example.com", password="testpassword")

#         # Create tenant and asanas/postures
#         self.tenant = Tenant.objects.create(client_name=self.trainer_user, slug="tenant_slug")
#         self.asana = Asana.objects.create(name="Example Asana", created_by=self.trainer_user, tenant=self.tenant,no_of_postures=3,created_at=timezone.now(),last_modified_at=timezone.now())
#         self.posture = Posture.objects.create(tenant=self.tenant,asana=self.asana, step_no=1)

#     def test_view_trained(self):
#         self.client.login(username="traineruser", password="testpassword") 
       

#       # Log in as trainer user
#         url = reverse('view-trained', kwargs={'slug': self.tenant.slug})  # Adjust the URL name as needed
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)  # Check for successful response
#         self.assertTemplateUsed(response, "users/view_trained.html")  # Check the template used
#         self.assertIn('trained_asanas', response.context)  # Check that trained_asanas is in context
#         self.assertEqual(len(response.context['trained_asanas']), 1)  # Check the number of trained asanas

#     def test_view_posture(self):
#         data=self.client.login(username="traineruser", password="testpassword") 
#         self.assertTrue(data) # Log in as trainer user
#         url = reverse('view-posture', kwargs={'asana_id': self.asana.id, 'slug': self.tenant.slug})  # Adjust the URL name as needed
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)  # Check for successful response
#         self.assertTemplateUsed(response, "users/view_posture.html")  # Check the template used
#         self.assertIn('postures', response.context)  # Check that postures is in context
#         self.assertEqual(len(response.context['postures']), 3)  # Check the number of postures

#         # You can also check for other context variables
#         self.assertEqual(response.context['tenant'], self.tenant)  # Check the tenant context variable




# from django.test import TestCase
# from django.urls import reverse
# from django.utils import timezone
# from django.contrib.auth.models import User
# from users.models import Asana, Posture, Tenant, TrainerLogDetail, Order, Subscription

# class CreateAsanaViewTest(TestCase):

#     def setUp(self):
#         # Create users
#         self.factory = RequestFactory()
#         self.trainer_user = User.objects.create_user(username="traineruser", password="testpassword")
        
#         # Ensure this user passes check_trainer
#         self.trainer_log = TrainerLogDetail.objects.create(trainer_name=self.trainer_user, tenant_id=1)

#         # Create a tenant for the test
#         self.tenant = Tenant.objects.create(slug="tenant_slug", client_name=self.trainer_user)
#         self.subscription = Subscription.objects.create(permitted_asanas=5, no_of_persons_onboard=4,price=100,created_at=timezone.now(),updated_at=timezone.now())
#         self.order = Order.objects.create(name=self.trainer_user, status='ACCEPT', subscription=self.subscription, amount=100,provider_order_id ="isdhfjsehfjsdhgjhdbj",payment_id="sifjiewuhgijehrjgherjghe",signature_id="akfjiesjfkjhsdjhfkjdshk",created_at=timezone.now(),updated_at=timezone.now())

#         self.asana = Asana.objects.filter(name='New Asana', tenant=self.tenant).first()
#         group = Group.objects.create(name='Trainer')
#         self.trainer_user.groups.add(group)


#         # Log in the user
        

#         # Trainer log detail
        


#     def test_post_create_asana(self):
#     # Ensure the user logs in successfully
#       login_success = self.client.login(username="traineruser", password="testpassword")
#       self.assertTrue(login_success, "Login failed!")

#     # Define the URL
#       url = reverse('create-asana', kwargs={'slug': self.tenant.slug})

#     # POST data simulating asana creation
#       post_data = {
#         'form-TOTAL_FORMS': '1',
#         'form-INITIAL_FORMS': '0',
#         'form-MIN_NUM_FORMS': '0',
#         'form-MAX_NUM_FORMS': '5',
#         'form-0-name': 'New Asana',
#         'form-0-no_of_postures': 3,
#     }

#     # Make POST request
#       response = self.client.post(url, post_data)

#     # Debugging: print response content if needed
#       print("Response content:", response.content)

#     # Ensure the response redirects (expected status code 302)
#       self.assertEqual(response.status_code, 302)

#     # Check that the asana was created in the database
#       asana = Asana.objects.filter(name='New Asana', tenant=self.tenant).first()
#       self.assertIsNotNone(asana, "Asana object was not created!")

#     # Check that the correct number of postures was created
#       self.assertEqual(asana.no_of_postures, 3)

#     # Verify that the correct number of postures were created
#       postures = Posture.objects.filter(asana=asana)
#       self.assertEqual(postures.count(), 3)

    
#     def test_get_create_asana_view(self):
#         login_success = self.client.login(username="traineruser", password="testpassword")
#         print(f"Login successful: {login_success}")

#         url = reverse('create-asana', kwargs={'slug': self.tenant.slug})

#         response = self.client.get(url)
        
        
#         self.assertEqual(response.status_code, 302)
#         self.assertTemplateUsed(response, 'users/create_asana.html')
#         self.assertIn('formset', response.context)
#         self.assertIn('tenant', response.context)
#         self.assertTrue(response.context['is_trainer'])

#     def test_post_update_asana(self):
#         self.assertTrue(self.client.login(username="traineruser", password="testpassword"))
#         # Create an existing asana to update
#         asana = Asana.objects.create(name="Existing Asana", created_by=self.trainer_user, tenant=self.tenant, no_of_postures=3, created_at=timezone.now(), last_modified_at=timezone.now())

#         url = reverse('create-asana', kwargs={'slug': self.tenant.slug}) + f"?update=true&asana_id={asana.id}"

#         # POST data simulating asana update
#         post_data = {
#             'asana_id': asana.id,
#             'name': 'Updated Asana',
#             'no_of_postures': 5,
#         }

#         response = self.client.post(url, post_data)

#         # Ensure the response redirects after updating the asana
#         self.assertEqual(response.status_code, 302)

#         # Check that the asana was updated in the database
#         asana.refresh_from_db()
#         self.assertEqual(asana.name, 'Updated Asana')
#         self.assertEqual(asana.no_of_postures, 5)

#         # Check that the postures were updated accordingly
#         postures = Posture.objects.filter(asana=asana)
#         self.assertEqual(postures.count(), 5)

#     def test_delete_asana(self):
#         self.assertTrue(self.client.login(username="traineruser", password="testpassword"))
#         # Create an existing asana to delete
#         asana = Asana.objects.create(name="Delete Asana", created_by=self.trainer_user, tenant=self.tenant, no_of_postures=3, created_at=timezone.now(), last_modified_at=timezone.now())

#         url = reverse('create-asana', kwargs={'slug': self.tenant.slug})

#         # POST data simulating asana deletion
#         post_data = {
#             'asana_id': asana.id,
#             'delete_asana': True,
#         }

#         response = self.client.post(url, post_data)
#         asana_exists = Asana.objects.filter(id=asana.id).exists()
#         self.assertFalse(asana_exists)


#         # Ensure the response redirects after deleting the asana
#         self.assertEqual(response.status_code, 302)

#         # Check that the asana was deleted from the database
        

#     def test_get_max_forms_with_trainer_log(self):
#         self.client.login(username="traineruser", password="testpassword")
#         # Create a TrainerLogDetail entry for the trainer
#         TrainerLogDetail.objects.create(trainer_name=self.trainer_user, tenant=self.tenant, no_of_asanas_created=2)

#         # Create a request for the view
#         request = self.factory.get(f'/create-asana/{self.tenant.slug}')
#         request.user = self.trainer_user

#         # Instantiate the view and call the get_max_forms method
#         view = CreateAsanaView()
#         max_forms, no_of_asanas_created_by_trainee = view.get_max_forms(request, slug=self.tenant.slug)

#         # Check that the max forms and asanas created match expected values
#         self.assertEqual(max_forms, 5)  # Subscription allows 5 asanas
#         self.assertEqual(no_of_asanas_created_by_trainee, 2)  # Trainer has already created 2 asanas

#     def test_get_max_forms_no_trainer_log(self):
#         self.client.login(username="traineruser", password="testpassword")
#         # No TrainerLogDetail entry exists for the trainer

#         # Create a request for the view
#         request = self.factory.get(f'/create-asana/{self.tenant.slug}')
#         request.user = self.trainer_user

#         # Instantiate the view and call the get_max_forms method
#         view = CreateAsanaView()
#         max_forms, no_of_asanas_created_by_trainee = view.get_max_forms(request, slug=self.tenant.slug)

#         # Check that no forms are allowed and no asanas created by trainer
#         self.assertEqual(max_forms, 0)  # No trainer log detail found
#         self.assertEqual(no_of_asanas_created_by_trainee, 0)  # No asanas created

#     def test_get_max_forms_no_order(self):
#         self.client.login(username="traineruser", password="testpassword")
#         # Delete the existing order to simulate the "no order" scenario
#         Order.objects.filter( name=self.trainer_user).delete()

#         # Create a request for the view
#         request = self.factory.get(f'/create-asana/{self.tenant.slug}')
#         request.user = self.trainer_user

#         # Instantiate the view and call the get_max_forms method
#         view = CreateAsanaView()
#         max_forms, no_of_asanas_created_by_trainee = view.get_max_forms(request, slug=self.tenant.slug)

#         # Check that max forms are 0 because there's no valid order for this trainer
#         self.assertEqual(max_forms, 0)  # No order found
#         self.assertEqual(no_of_asanas_created_by_trainee, 0)  # Default value

#     @patch('users.views.capture_exception')
#     def test_get_max_forms_with_exception(self, mock_capture_exception):
#         self.client.login(username="traineruser", password="testpassword")
#         # Simulate an exception during the execution
#         with patch('users.models.TrainerLogDetail.objects.filter', side_effect=Exception('Error!')):
#             request = self.factory.get(f'/create-asana/{self.tenant.slug}')
#             request.user = self.trainer_user

#             view = CreateAsanaView()
#             max_forms, no_of_asanas_created_by_trainee = view.get_max_forms(request, slug=self.tenant.slug)

#             # Check that in case of exception, max_forms and no_of_asanas_created_by_trainee are set to 0
#             self.assertEqual(max_forms, 0)
#             self.assertEqual(no_of_asanas_created_by_trainee, 0)

#             # Ensure that capture_exception was called with the exception
#             mock_capture_exception.assert_called_once()

       
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from users.models import Tenant, CourseDetails, Posture, Subscription
from django.utils import timezone

class CourseCreationViewTests(TestCase):

    def setUp(self):
        # Create a user and assign the 'Trainer' group to the user
        self.user_client=User.objects.create(username="clientuser",password="123")
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.tenant = Tenant.objects.create(client_name=self.user_client, slug="test-tenant")
        self. course = CourseDetails.objects.create(user=self.user, tenant=self.tenant, course_name="Test Course")

        
        self.trainer_group = Group.objects.create(name='Trainer')
        self.user.groups.add(self.trainer_group)
        
        # Create a tenant
      
        # Log in the user for authenticated tests
        self.client.login(username='testuser', password='12345')

    def test_course_creation_view_get(self):
        """Test the GET request for the course creation view without course_id"""
        url = reverse('create-course', kwargs={'slug': self.tenant.slug})
        response = self.client.get(url)

        # Ensure the view renders with status 200
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'users/trainer_dashboard.html')

        # Check the context
        self.assertTrue(response.context['is_trainer'])
        self.assertEqual(response.context['tenant'], self.tenant)

    def test_course_creation_view_get_with_course_id(self):
        """Test the GET request for the course creation view with course_id"""
        # Create a course for the user
       

        url = reverse('create-course', kwargs={'slug': self.tenant.slug})
        response = self.client.get(url)

        # Ensure the view renders with status 200
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'users/trainer_dashboard.html')

        # Check the context
        self.assertEqual(response.context['course_id'], self.course.id)
        self.assertTrue(response.context['is_trainer'],True)
        self.assertEqual(response.context['tenant'], self.tenant)

    def test_course_creation_view_post_valid(self):
        """Test a valid POST request for course creation"""
        url = reverse('create-course', kwargs={'slug': self.tenant.slug})
        data = {
              'course_name': 'New course',
                'description': 'sjfnksdnmds',
                  'user': self.user.id,  # You can pass the user's ID here
                   'tenant': self.tenant.id,  # You can pass the tenant's ID here
}
        response = self.client.post(url, data)

        
        

        # Ensure the course is created
        self.assertEqual(CourseDetails.objects.count(), 1)
        
        # Ensure the user is redirected after form submission
        self.assertRedirects(response, reverse('create-course', kwargs={'slug': self.tenant.slug}))

    def test_course_creation_view_post_invalid(self):
        """Test an invalid POST request for course creation"""
        url = reverse('create-course', kwargs={'slug': self.tenant.slug})
        data = {
            'name': '',  # Invalid form data (e.g., missing name)
        }
        response = self.client.post(url, data)

        # The form should be invalid, and the same page should be rendered
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/trainer_dashboard.html')
        self.assertFalse(response.context['form'].is_valid())

    def test_delete_course(self):
        """Test course deletion via POST request"""
        # Create a course
        course = CourseDetails.objects.create(user=self.user, tenant=self.tenant, course_name="Test Course")

        url = reverse('create-course', kwargs={'slug': self.tenant.slug})
        data = {
            'delete_course': 'true',
            'course_id': course.id
        }
        response = self.client.post(url, data)

        # Ensure the course is deleted
        self.assertEqual(CourseDetails.objects.count(), 0)

        # Ensure the user is redirected after deletion
        self.assertRedirects(response, reverse('create-course', kwargs={'slug': self.tenant.slug}))





class StaffDashboardFunctionTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='staffuser', password='12345')
        self.trainer_group = Group.objects.create(name='Trainer')
        self.user.groups.add(self.trainer_group)
        self.user_client=User.objects.create(username="clientuser",password="123")
        self.tenant = Tenant.objects.create(client_name=self.user_client, slug="test-tenant")


        # Log in the user for authenticated tests
        self.client.login(username='staffuser', password='12345')

    def test_staff_dashboard_function(self):
        url = reverse('staff_dashboard', kwargs={'slug': self.tenant.slug})
        response = self.client.get(url)

        # Ensure the view renders with status 200
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'users/staff_dashboard.html')

        # Check context
        self.assertTrue(response.context['is_trainer'])
        self.assertEqual(response.context['tenant'], self.tenant)






class EditPostureViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='trainer', password='12345')
        self.trainer_group = Group.objects.create(name='Trainer')
        self.user.groups.add(self.trainer_group)
        self.user_client=User.objects.create(username="clientuser",password="123")
        self.tenant = Tenant.objects.create(client_name=self.user_client, slug="test-tenant")

        self.asana=Asana.objects.create(name="asana",no_of_postures=1, created_by=self.user_client, created_at=timezone.now(),last_modified_at=timezone.now(),tenant=self.tenant)
        
        self.posture = Posture.objects.create(asana=self.asana, step_no=1,tenant=self.tenant,is_active=True)  # Sample data

        # Log in the user for authenticated tests
        self.client.login(username='trainer', password='12345')

    def test_edit_posture_get(self):
        url = reverse('edit-posture', kwargs={'slug': self.tenant.slug, 'posture_id': self.posture.id})
        response = self.client.get(url)

        # Ensure the view renders with status 200
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'users/edit_posture.html')

        # Check context
        self.assertEqual(response.context['posture'], self.posture)
        self.assertEqual(response.context['tenant'], self.tenant)
