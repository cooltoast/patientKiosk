import datetime
from django import forms
from .models import Doctor, Patient, Appointment, Office, ExamRoom

class OfficeForm(forms.Form):
  office = forms.ModelChoiceField(queryset=Office.objects.all(), empty_label="(Select Office)")

class AppointmentForm(forms.Form):
  today = datetime.datetime.today()
  appointment = forms.ModelChoiceField(queryset=Appointment.objects.filter(scheduled_time__month=today.month, scheduled_time__day=today.day, is_break=False), empty_label="(Select Appointment)")


class NewAppointmentForm(forms.Form):
  scheduled_time = forms.TimeField()
  duration = forms.IntegerField()
  doctor = forms.ModelChoiceField(queryset=Doctor.objects.all())
  patient = forms.ModelChoiceField(queryset=Patient.objects.all())
  office = forms.ModelChoiceField(queryset=Office.objects.filter(is_active=True))
  exam_room = forms.ModelChoiceField(queryset=Office.objects.get(is_active=True).examroom_set.all())

  def create_appt(self):
    print 'yo'
    pass
