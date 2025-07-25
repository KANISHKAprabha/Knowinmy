# Generated by Django 4.1.2 on 2024-10-05 08:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asana',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Asana Name')),
                ('no_of_postures', models.PositiveIntegerField(verbose_name='Number of Postures')),
                ('created_at', models.DateTimeField(verbose_name='Created At')),
                ('last_modified_at', models.DateTimeField(verbose_name='Last Modified At')),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teaching_asans', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
            ],
        ),
        migrations.CreateModel(
            name='CourseDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Course Name')),
                ('description', models.TextField(max_length=200)),
                ('created_at', models.DateTimeField(null=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(null=True, verbose_name='Last modified at')),
                ('asanas_by_trainer', models.ManyToManyField(related_name='asanas_created_by_trainee', to='users.asana')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=100)),
                ('permitted_asanas', models.PositiveIntegerField(default=None)),
                ('no_of_persons_onboard', models.PositiveIntegerField(default=None)),
                ('price', models.FloatField(default=None)),
                ('highlight_status', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(null=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(null=True, verbose_name='Last modified at')),
            ],
        ),
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_name', models.CharField(max_length=100)),
                ('domain_name', models.CharField(max_length=100, unique=True)),
                ('organization_email', models.EmailField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('full_url', models.URLField(blank=True)),
                ('client_name', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TrainerLogDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_of_asanas_created', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('created_at', models.DateTimeField(null=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(null=True, verbose_name='Last modified at')),
                ('onboarded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='onboard_traines_by', to=settings.AUTH_USER_MODEL)),
                ('tenant', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='users.tenant')),
                ('trainer_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trainees', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudentLogDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(null=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(null=True, verbose_name='Last modified at')),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='enrollments_added', to=settings.AUTH_USER_MODEL)),
                ('mentor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.trainerlogdetail')),
                ('student_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student', to=settings.AUTH_USER_MODEL)),
                ('tenant', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='users.tenant')),
            ],
        ),
        migrations.CreateModel(
            name='Posture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_no', models.PositiveIntegerField(verbose_name='Step No')),
                ('name', models.CharField(max_length=100, verbose_name='Posture Name')),
                ('dataset', models.FileField(blank=True, null=True, upload_to='')),
                ('snap_shot', models.ImageField(blank=True, null=True, upload_to='images/', verbose_name='Snap Shot')),
                ('last_modified_at', models.DateTimeField(null=True, verbose_name='Last Modified At')),
                ('first_trained_at', models.DateTimeField(null=True, verbose_name='First Trained At')),
                ('is_active', models.BooleanField(default=True)),
                ('asana', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_postures', to='users.asana')),
                ('tenant', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='users.tenant')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254, verbose_name='Customer Name')),
                ('amount', models.FloatField(verbose_name='Amount')),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('ACCEPT', 'ACCEPT'), ('REJECT', 'REJECT')], default='PENDING', max_length=10, verbose_name='Payment Status')),
                ('provider_order_id', models.CharField(max_length=40, verbose_name='Order ID')),
                ('payment_id', models.CharField(max_length=36, verbose_name='Payment ID')),
                ('signature_id', models.CharField(max_length=128, verbose_name='Signature ID')),
                ('created_at', models.DateTimeField(null=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(null=True, verbose_name='Last modified at')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='users.subscription')),
            ],
        ),
        migrations.CreateModel(
            name='EnrollmentDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(null=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(null=True, verbose_name='Last modified at')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('students_added_to_courses', models.ManyToManyField(blank=True, related_name='course_asanas', to='users.coursedetails')),
                ('tenant', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='users.tenant')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='enrolled_courses', to=settings.AUTH_USER_MODEL, verbose_name='Student Name')),
            ],
        ),
        migrations.AddField(
            model_name='coursedetails',
            name='tenant',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='users.tenant'),
        ),
        migrations.AddField(
            model_name='coursedetails',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trainee_name', to=settings.AUTH_USER_MODEL, verbose_name='Trainee Name'),
        ),
        migrations.CreateModel(
            name='CouponCodeForNegeotiation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discounted_price', models.FloatField(default=0)),
                ('code', models.CharField(blank=True, max_length=8, null=True, unique=True)),
                ('created_at', models.DateTimeField(null=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(null=True, verbose_name='Last modified at')),
                ('subscription_for_coupon_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.subscription')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupon_code_for_client', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ClientOnboarding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trainers_onboarded', models.IntegerField(default=0)),
                ('students_onboarded', models.IntegerField(default=0)),
                ('client', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('tenant', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='users.tenant')),
            ],
        ),
        migrations.AddField(
            model_name='asana',
            name='tenant',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='users.tenant'),
        ),
    ]
