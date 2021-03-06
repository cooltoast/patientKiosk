from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^login_redirect/', views.login_redirect, name='login_redirect'),
    url(r'^checkin/', views.checkin, name='checkin'),
    url(r'^checkin_appt/', views.checkin_appt, name='checkin_appt'),
    url(r'^set_office/', views.set_office, name='set_office'),
    url(r'^new_appt/', views.NewAppointmentFormView.as_view(), name='new_appt'),
    url(r'^new_patient/', views.NewPatientFormView.as_view(), name='new_patient'),
    url(r'^refresh_appts/', views.refresh_appts, name='refresh_appts'),
    url(r'^refresh_patients/', views.refresh_patients, name='refresh_patients'),
    url(r'^validate_patient_form/', views.validate_patient_form, name='validate_patient_form'),
    url(r'^validate_patient_form_new_appt/', views.validate_patient_form_new_appt, name='validate_patient_form_new_appt'),
    url(r'^logout/', views.logout, name='logout'),
]
