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

  try:
    exam_room = forms.ModelChoiceField(queryset=Office.objects.get(is_active=True).examroom_set.all())
  except Office.DoesNotExist as e:
    print e

  def create_appt(self):
    print 'yo'
    pass

class NewPatientForm(forms.Form):
  first_name = forms.CharField()
  last_name = forms.CharField()
  gender = forms.ChoiceField(choices=(('Female', 'Female'),('Male', 'Male'),('Other', 'Other')))
  doctor = forms.ModelChoiceField(queryset=Doctor.objects.all())
  date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=[n for n in range(datetime.datetime.now().year, 1898, -1)]))
  email = forms.EmailField()

  def create_patient(self):
    print 'yo'
    pass
