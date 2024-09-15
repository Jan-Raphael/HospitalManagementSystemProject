from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import PatientAccount, DoctorAccount

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class PatientSignupForm(forms.ModelForm):
    class Meta:
        model = PatientAccount
        fields = ['phone_number', 'address']

class DoctorSignupForm(forms.ModelForm):
    class Meta:
        model = DoctorAccount
        fields = ['specialty', 'qualification', 'years_of_experience']

class PatientLoginForm(AuthenticationForm):
    class Meta:
        model = PatientAccount
        fields = ['username', 'password']

class DoctorLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)