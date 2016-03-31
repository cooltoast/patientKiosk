import datetime
from django import forms
from .models import Appointment

class AppointmentForm(forms.Form):
  today = datetime.datetime.today()
  appointment = forms.ModelChoiceField(queryset=Appointment.objects.filter(scheduled_time__month=today.month, scheduled_time__day=today.day, is_break=False), empty_label="(Select Appointment)")
