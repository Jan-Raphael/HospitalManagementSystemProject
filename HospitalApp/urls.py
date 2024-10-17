from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('patient_signup/', views.patient_signup, name='patient_signup'),
    path('doctor_signup/', views.doctor_signup, name='doctor_signup'),
    path('login/', views.login_view, name='login_view'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient_dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/logout/', views.doctor_logout, name='doctor_logout'),
    path('login/patient/', views.patient_login, name='patient_login'),
    path('login/doctor/', views.doctor_login, name='doctor_login'),
                  path('doctor/waiting/', views.waiting_for_approval, name='waiting_for_approval'),
    path('patient/schedule-appointment/', views.schedule_appointment, name='schedule_appointment'),
    path('patient/view-appointments/', views.view_appointments, name='view_appointments'),
    path('doctor/view-appointments/', views.doctor_view_appointments, name='doctor_view_appointments'),
    path('patient/verify-account/', views.verify_account, name='verify_account'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
path('patient/upload-medical-records/', views.upload_medical_records, name='upload_medical_records'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
