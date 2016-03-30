from __future__ import unicode_literals

from django.db import models
import datetime

# Create your models here.
class Doctor(models.Model):
  name = models.CharField(max_length=200)
  doctor_id = models.IntegerField(default=0)
  access_token = models.CharField(max_length=200)
  refresh_token = models.CharField(max_length=200)
  expires_timestamp = models.DateTimeField()


class Patient(models.Model):
  name = models.CharField(max_length=200)
  doctor = models.ForeignKey(Doctor, default=None, on_delete=models.CASCADE)
  patient_id = models.IntegerField(default=0)
  date_of_birth = models.DateTimeField(default=datetime.datetime.now)
  email = models.EmailField(default=None)
  #add more fields


class Appointment(models.Model):
  start_time = models.DateTimeField()
  end_time = models.DateTimeField()
  doctor = models.ForeignKey(Doctor, default=None, on_delete=models.CASCADE)
  patient = models.ForeignKey(Patient, default=None, blank=True, null=True, on_delete=models.CASCADE)
  is_break = models.BooleanField(default=False)
