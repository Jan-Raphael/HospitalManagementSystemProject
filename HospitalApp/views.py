from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from AdminHospitalApp.forms import UserForm
from .forms import PatientSignupForm, PatientVerificationForm, DoctorSignupForm, PatientLoginForm, DoctorLoginForm, AppointmentForm, VerifyAccountForm
from .models import PatientAccount, DoctorAccount, Appointment
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UserForm, PatientAccountForm, VerifyAccountForm  # Ensure these are correctly imported

def is_doctor(user):
    return hasattr(user, 'doctoraccount')

def is_patient(user):
    return hasattr(user, 'patientaccount')

@login_required
@user_passes_test(is_doctor)
def doctor_dashboard(request):
    doctor_profile = DoctorAccount.objects.get(user=request.user)
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

def doctor_signup(request):
    if request.method == 'POST':
        form = DoctorSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('doctor_dashboard')  # Redirect to the doctor's dashboard
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
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and hasattr(user, 'doctoraccount'):
                login(request, user)
                return redirect('doctor_dashboard')
            else:
                form.add_error(None, 'Invalid credentials or user is not a doctor')
    else:
        form = AuthenticationForm()
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
    doctor = DoctorAccount.objects.get(user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date')
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