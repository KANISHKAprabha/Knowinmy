from django.apps import apps
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .resources import PersonResource
from django_celery_results.models import TaskResult


class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        self.search_fields = [field.name for field in model._meta.fields]
        super(ListAdminMixin, self).__init__(model, admin_site)


models = apps.get_models()
for model in models:
    admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
    try:
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass



from django.db.models import Sum
from .models import CourseDetails, EnrollmentDetails, Subscription, TrainerLogDetail, StudentLogDetail, ClientOnboarding

class CustomAdminSite(admin.AdminSite):
    site_header = 'Custom Admin Dashboard'
    index_title = 'Dashboard'
    site_title = 'My Admin'

    def index(self, request, extra_context=None):
        # Add custom context here
        context = {
            'courses_count': CourseDetails.objects.count(),
            'enrollments_count': EnrollmentDetails.objects.count(),
            'subscriptions_count': Subscription.objects.count(),
            'trainers_count': TrainerLogDetail.objects.count(),
            'students_count': StudentLogDetail.objects.count(),
            'asanas_count': TrainerLogDetail.objects.aggregate(total_asanas=Sum('no_of_asanas_created'))['total_asanas'] or 0,
        }
        return super().index(request, extra_context={**context, **(extra_context or {})})

admin_site = CustomAdminSite(name='custom_admin')

admin_site.register(CourseDetails)
admin_site.register(EnrollmentDetails)
admin_site.register(Subscription)
admin_site.register(TrainerLogDetail)
admin_site.register(StudentLogDetail)
admin_site.register(ClientOnboarding)





class PersonAdmin(ImportExportModelAdmin):
    resource_class = PersonResource
