from dataclasses import field
from pyexpat import model
from django.forms import Form,ModelForm,Textarea
from .models import *
from django.contrib.auth.forms import SetPasswordForm
# import the standard Django Forms
# from built-in library
from django import forms 

class AsanaCreationForm(ModelForm):
    class Meta:
        model = Asana
        fields = ['name', 'no_of_postures']

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)  # Extract tenant from kwargs
        super(AsanaCreationForm, self).__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super(AsanaCreationForm, self).save(commit=False)
        if self.tenant:
            instance.tenant = self.tenant  # Assign the tenant to the instance
        if commit:
            instance.save()
        return instance

class EditPostureForm(ModelForm):
    class Meta:
        model = Posture
        fields = ['name', 'snap_shot']

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super(EditPostureForm, self).__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super(EditPostureForm, self).save(commit=False)
        if self.tenant:
            instance.tenant = self.tenant  # Assign the tenant
        if commit:
            instance.save()
        return instance

        
# class CouponCodeForm(ModelForm):
#     class Meta:
#         model=
#         fields=[]


class StudentCourseMappingForm(ModelForm):
    class Meta:
        model = EnrollmentDetails
        fields = ['user', 'students_added_to_courses']

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        print(self.tenant,"line 57jhdk")
        self.trainer_user = kwargs.pop('user', None)
        print(self.trainer_user,"line 58  kjghskj")
        super(StudentCourseMappingForm, self).__init__(*args, **kwargs)
        
        if self.tenant and self.trainer_user:
            trainee_ids = TrainerLogDetail.objects.filter(tenant=self.tenant,trainer_name=self.trainer_user).first()
            trainer=TrainerLogDetail.objects.get(trainer_name=self.trainer_user)
            print(trainer,"line 65 forms ")
            print(trainee_ids,"loesfjkesjh")    
            if  trainee_ids == None:
                print("ids not found ")
            client_name = trainee_ids.onboarded_by
            print(client_name,"line no 66 in forms s")
            self.fields['user'] = forms.ModelChoiceField(
                queryset=StudentLogDetail.objects.filter(mentor=trainer, tenant=self.tenant),
                initial=self.instance.user if self.instance.pk else None
            )
            
            print(self.fields['user'],"line no 67 in forms ")
            self.fields['students_added_to_courses'] = forms.ModelMultipleChoiceField(
                queryset=CourseDetails.objects.filter(tenant=self.tenant,user=self.trainer_user),
                widget=forms.CheckboxSelectMultiple,initial=self.instance.user if self.instance.pk else None
            )



    def clean_user(self):
        user = self.cleaned_data.get('user')
        if isinstance(user, StudentLogDetail):
            print(user,"line no 60 in forms.py")
            return user.student_name 
        return user
           
            
    



class CourseCreationForm(forms.ModelForm):
    class Meta:
        model = CourseDetails
        fields = ['course_name', 'description', 'asanas_by_trainer']

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        print(kwargs,"line 9333")
        print(args,"line 944444")
        print(self.tenant,"line 93 forms.py")
        self.user = kwargs.pop('user', None)
        print(self.user,"line 94")
        super(CourseCreationForm, self).__init__(*args, **kwargs)

        if self.tenant and self.user:
            print(self.tenant,"line no 102 ")
            self.fields['asanas_by_trainer'] = forms.ModelMultipleChoiceField(
                queryset=Asana.objects.filter( tenant=self.tenant,created_by=self.user,),
                widget=forms.CheckboxSelectMultiple,initial=self.instance.user if self.instance.pk else None
            )
            print(self.user,"line 105 in forms.py")
            print(self.fields['asanas_by_trainer'] ,"line no 102 in forms.py ")
        self.fields['description'].widget = forms.Textarea(attrs={'rows': 2})

    def save(self, commit=True):
        instance = super(CourseCreationForm, self).save(commit=False)
        if self.tenant:
            instance.tenant = self.tenant  # Assign the tenant
        if commit:
            instance.save()
        return instance




class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['subscription', 'name', 'amount', 'status']

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super(OrderForm, self).__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super(OrderForm, self).save(commit=False)
        if self.tenant:
            instance.tenant = self.tenant  # Assign the tenant
        if commit:
            instance.save()
        return instance


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = [ 'permitted_asanas', 'no_of_persons_onboard','duration_in_months']

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super(SubscriptionForm, self).__init__(*args, **kwargs)
        self.fields['subscription_id'] = forms.CharField(widget=forms.HiddenInput(), required=False)
    def save(self, commit=True):
        instance = super(SubscriptionForm, self).save(commit=False)
        if not instance.id:
            print(id,"oooooooooooooooooooooooformmmmmmmmmm")
            last_subscription = Subscription.objects.order_by('id').last()
            if last_subscription:
                instance.id = last_subscription.id + 1
            else:
                instance.id = 1 
       

        if commit:
            instance.save()
        return instance




class OrganisationForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['client_name', 'organization_name', 'domain_name', 'organization_email']

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        self.user = kwargs.pop('user', None)  # Get the user from the kwargs
        super(OrganisationForm, self).__init__(*args, **kwargs)
        
        if self.user:
            self.fields['client_name'].initial = self.user  # Set client_name to the request.user
            self.fields['client_name'].widget = forms.HiddenInput()  

    def save(self, commit=True):
        instance = super(OrganisationForm, self).save(commit=False)
        if self.tenant:
            instance.tenant = self.tenant  # Assign the tenant
        if self.user:
            instance.client_name = self.user  # Assign request.user to client_name
        if commit:
            instance.save()
        return 
    


# class SlugEditForm(forms.ModelForm):
#     class Meta:
#         model=Tenant














class UserOnboardingForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('trainer', 'Trainer'),
        ('student', 'Student')
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES)
   

    class Meta:
        model = User
        fields = ['username','first_name', 'last_name', 'email', 'role']
    def __init__(self, *args, **kwargs):
        print(args,"arguments")
        print(kwargs,"line no 217")
        self.user = kwargs.pop('user', None)
        print(self.user,"pppppppppppppppppp")
        self.tenant = kwargs.pop('tenant', None)
        
        super(UserOnboardingForm, self).__init__(*args, **kwargs)

        # Debug print statement to see if user and tenant are provided
        print(f"User: {self.user}, Tenant: {self.tenant}")

        # Ensure the user and tenant are valid
        if self.user and  self.tenant :
            print("Adding mentor field")

            self.fields['mentor'] = forms.ModelChoiceField(
                queryset=TrainerLogDetail.objects.filter(tenant=self.tenant, onboarded_by=self.user),
                widget=forms.Select,  # Change to a dropdown
                empty_label="Select a mentor" ,
                 required=False # Optional placeholder
            )
        else:
           
            print("User or tenant is missing. Mentor field not added.")
        
    def save(self, commit=True):
        instance = super(UserOnboardingForm, self).save(commit=False)
        # self.fields['mentor']=forms.CheckboxInput(queryset=StudentLogDetail.objects.create(tenant=self.tenant,mentor=))
        if self.tenant:
            instance.tenant = self.tenant 

        
           
           

        if commit:
            instance.save()
        return instance




class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name','last_name']
    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        print(kwargs,"line 93")
        print(args,"line 94")
        print(self.tenant,"line 93 forms.py")
        self.user = kwargs.pop('user', None)
        print(self.user,"line 94")
        super(UserEditForm, self).__init__(*args, **kwargs)

        
            
        

    def save(self, commit=True):
        instance = super(UserEditForm, self).save(commit=False)
        if self.tenant:
            instance.tenant = self.tenant  # Assign the tenant
        if commit:
            instance.save()
        return instance




class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address', 'city', 'state', 'country', 'phone_number']

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)  



class SlugChangeRequestForm(forms.ModelForm):
    slug_change_requested = forms.SlugField(label="New Slug", max_length=50, required=True)

    class Meta:
        model = Tenant
        fields = ['slug_change_requested']




class SubscriptionChangeForm(forms.Form):
    request_type = forms.ChoiceField(
        choices=[('change', 'Change Subscription'), ('withdraw', 'Withdraw Subscription')],
        required=True,
        label="Request Type"
    )
    reason = forms.CharField(widget=forms.Textarea, required=True, label="Reason for Request")











class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        
        # Customizing each field in the form
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control custom-input',  # Add your CSS classes
            'placeholder': 'Enter new password',
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control custom-input',
            'placeholder': 'Confirm new password',
        })
        
    # Custom error messages
    error_messages = {
        'password_mismatch': "The two password fields didn’t match.",
    }
