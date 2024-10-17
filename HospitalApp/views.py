from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from HospitalApp.models import PatientAccount
from .forms import DoctorLoginForm, DoctorSignupForm
from .forms import PatientSignupForm, AppointmentForm
from .forms import UserForm, PatientAccountForm, VerifyAccountForm
from .models import Appointment
from .models import DoctorAccount


def is_doctor(user):
    return hasattr(user, 'doctoraccount') and user.doctoraccount.is_doctor

def is_patient(user):
    return hasattr(user, 'patientaccount')

@login_required
@user_passes_test(is_doctor)
def doctor_dashboard(request):
    doctor_profile = DoctorAccount.objects.get(user=request.user)
    if not doctor_profile.is_approved:
        return redirect('waiting_for_approval')
    return render(request, 'DoctorsAccount/doctor_dashboard.html', {'doctor_profile': doctor_profile})


@login_required
@user_passes_test(is_patient)
def patient_dashboard(request):
    return render(request, 'DoctorsAccount/patient_dashboard.html')

def home(request):
    return render(request, 'UserView/home.html')

def signup(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            login(request, user)
            return redirect('home')
    else:
        user_form = UserCreationForm()
    return render(request, 'AccountView/signup.html', {'user_form': user_form})

def patient_signup(request):
    if request.method == 'POST':
        form = PatientSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone_number = form.cleaned_data.get('phone_number')
            address = form.cleaned_data.get('address')

            patient_account = PatientAccount(user=user, phone_number=phone_number, address=address)
            patient_account.save()

            login(request, user)
            return redirect('patient_dashboard')
    else:
        form = PatientSignupForm()
    return render(request, 'AccountView/patient_signup.html', {'form': form})

# views.py
def doctor_signup(request):
    if request.method == 'POST':
        form = DoctorSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Set user to inactive until approved
            user.save()
            DoctorAccount.objects.create(
                user=user,
                specialty=form.cleaned_data['specialty'],
                qualification=form.cleaned_data['qualification'],
                years_of_experience=form.cleaned_data['years_of_experience'],
                is_doctor=True,
                is_approved=False  # Set to false initially
            )
            # Optionally send an email notification to admin for approval
            return render(request, 'DoctorsAccount/waiting_for_approval.html')  # Redirect to waiting page
    else:
        form = DoctorSignupForm()
    return render(request, 'AccountView/doctor_signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            pass
    return render(request, 'AccountView/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def patient_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and hasattr(user, 'patientaccount'):
                login(request, user)
                return redirect('patient_dashboard')  # Redirect to patient dashboard
            else:
                form.add_error(None, 'Invalid credentials or not a patient account')
    else:
        form = AuthenticationForm()
    return render(request, 'AccountView/patient_login.html', {'form': form})
def doctor_login(request):
    if request.method == 'POST':
        form = DoctorLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and hasattr(user, 'doctoraccount'):
                if user.doctoraccount.is_approved:
                    login(request, user)
                    return redirect('doctor_dashboard')
                else:
                    login(request, user)
                    messages.warning(request, "Your account is pending approval. Please wait for admin approval.")
                    return redirect('waiting_for_approval')
            else:
                form.add_error(None, 'Invalid credentials or user is not a doctor')
    else:
        form = DoctorLoginForm()
    return render(request, 'AccountView/doctor_login.html', {'form': form})


def doctor_logout(request):
    """Logs out the doctor and redirects to the home page."""
    logout(request)
    return redirect('home')

@login_required
@user_passes_test(is_patient)
def schedule_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()
            return redirect('patient_dashboard')
    else:
        form = AppointmentForm()
    return render(request, 'PatientView/schedule_appointment.html', {'form': form})

@login_required
@user_passes_test(is_patient)
def view_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by('-appointment_date')
    return render(request, 'PatientView/view_appointments.html', {'appointments': appointments})

@login_required
@user_passes_test(is_doctor)
def doctor_view_appointments(request):
    doctor_profile = DoctorAccount.objects.get(user=request.user)
    if not doctor_profile.is_approved:
        return redirect('waiting_for_approval')
    appointments = Appointment.objects.filter(doctor=doctor_profile).order_by('-appointment_date')
    return render(request, 'DoctorsAccount/doctor_view_appointments.html', {'appointments': appointments})
@login_required
def verify_account(request):
    try:
        patient_account = request.user.patientaccount
    except PatientAccount.DoesNotExist:
        messages.error(request, "Patient account does not exist.")
        return redirect('home')  # Redirect to a suitable page

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        patient_form = PatientAccountForm(request.POST, request.FILES, instance=patient_account)
        verify_form = VerifyAccountForm(request.POST)

        if user_form.is_valid() and patient_form.is_valid() and verify_form.is_valid():
            user_form.save()
            patient_form.save()
            patient_account.verification_status = True
            patient_account.save()
            messages.success(request, "Your account has been verified successfully.")
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserForm(instance=request.user)
        patient_form = PatientAccountForm(instance=patient_account)
        verify_form = VerifyAccountForm()

    context = {
        'user_form': user_form,
        'patient_form': patient_form,
        'verify_form': verify_form,
        'patient_account': patient_account,
    }
    return render(request, 'PatientView/verify_account.html', context)
@login_required
def upload_medical_records(request):
    if request.method == 'POST':
        medical_record_file = request.FILES.get('medical_records')
        if medical_record_file:
            patient_account = request.user.patientaccount
            patient_account.medical_records = medical_record_file
            patient_account.save()
            return redirect('patient_dashboard')
    return redirect('patient_dashboard')

@login_required
@user_passes_test(is_doctor)
def waiting_for_approval(request):
    doctor_profile = DoctorAccount.objects.get(user=request.user)
    context = {
        'doctor_profile': doctor_profile,
    }
    return render(request, 'DoctorsAccount/waiting_for_approval.html', context)
