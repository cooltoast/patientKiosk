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

  def __str__(self):
    return '%s, %s' % (self.name, self.date_of_birth.date())


class Appointment(models.Model):
  appointment_id = models.CharField(default='', max_length=200)
  scheduled_time = models.DateTimeField()
  duration = models.IntegerField(default=0)
  end_time = models.DateTimeField()
  doctor = models.ForeignKey(Doctor, default=None, on_delete=models.CASCADE)
  patient = models.ForeignKey(Patient, default=None, blank=True, null=True, on_delete=models.CASCADE)
  exam_room = models.IntegerField(default=-1)
  office = models.IntegerField(default=-1)
  is_break = models.BooleanField(default=False)

  def __unicode__(self):
    if (self.is_break):
      return '%s, Break time' % self.scheduled_time
    else:
      return '%s, %s' % (self.scheduled_time, self.patient.name)
