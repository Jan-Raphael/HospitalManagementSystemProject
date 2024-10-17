from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import PatientAccount, Appointment


class AppointmentForm(forms.ModelForm):
    appointment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_type']

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class PatientSignupForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'phone_number', 'address']


class DoctorSignupForm(UserCreationForm):
    specialty = forms.CharField(max_length=100)
    qualification = forms.CharField(widget=forms.Textarea, required=False)
    years_of_experience = forms.IntegerField(min_value=1)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'specialty', 'qualification', 'years_of_experience']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            DoctorAccount.objects.create(
                user=user,
                specialty=self.cleaned_data['specialty'],
                qualification=self.cleaned_data['qualification'],
                years_of_experience=self.cleaned_data['years_of_experience'],
                is_doctor=True,
                is_approved=False  # Ensure the account starts as unapproved
            )
        return user

class PatientLoginForm(AuthenticationForm):
    class Meta:
        model = PatientAccount
        fields = ['username', 'password']

class DoctorLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

class PatientVerificationForm(forms.ModelForm):
    class Meta:
        model = PatientAccount
        fields = ['profile_photo', 'medical_records_photo', 'phone_number', 'address']
        widgets = {
            'profile_photo': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'medical_records_photo': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

from django import forms
from django.contrib.auth.models import User
from HospitalApp.models import PatientAccount, DoctorAccount


class UserForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False, label='First Name')
    last_name = forms.CharField(max_length=30, required=False, label='Last Name')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class PatientAccountForm(forms.ModelForm):
    class Meta:
        model = PatientAccount
        fields = ['phone_number', 'address', 'profile_photo', 'medical_records_photo']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'profile_photo': forms.ClearableFileInput(attrs={'accept': 'image/*', 'class': 'form-control-file'}),
            'medical_records_photo': forms.ClearableFileInput(attrs={'accept': 'image/*', 'class': 'form-control-file'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class VerifyAccountForm(forms.Form):
    # This form can include a confirmation checkbox or any additional fields if needed
    confirm = forms.BooleanField(required=True, label='I confirm that the above information is correct.')