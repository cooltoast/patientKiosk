import datetime
from django import forms
from .models import Doctor, Patient, Appointment

class AppointmentForm(forms.Form):
  today = datetime.datetime.today()
  appointment = forms.ModelChoiceField(queryset=Appointment.objects.filter(scheduled_time__month=today.month, scheduled_time__day=today.day, is_break=False), empty_label="(Select Appointment)")

from django import forms

class NewAppointmentForm(forms.Form):
    scheduled_time = forms.TimeField()
    duration = forms.IntegerField()
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all())
    patient = forms.ModelChoiceField(queryset=Patient.objects.all())
    exam_room = forms.IntegerField()
    office = forms.IntegerField()

    def create_appt(self):
        print 'yo'
        pass
