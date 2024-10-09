from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import PatientAccount, DoctorAccount, Appointment
from django.utils import timezone


class AppointmentForm(forms.ModelForm):
    appointment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']  # This format matches the 'datetime-local' input
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
            # Create and link the doctor profile to the user
            DoctorAccount.objects.create(
                user=user,
                specialty=self.cleaned_data['specialty'],
                qualification=self.cleaned_data['qualification'],
                years_of_experience=self.cleaned_data['years_of_experience'],
                is_doctor=True
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