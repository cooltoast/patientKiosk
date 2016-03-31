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

  def __unicode__(self):
    return '%s, %s' % (self.name, self.doctor_id)

class Office(models.Model):
  name = models.CharField(max_length=200,default='')
  office_id = models.IntegerField(default=-1)
  doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
  is_active = models.BooleanField(default=False)

  def __unicode__(self):
    return '%s, id: %s, is_active: %s' % (self.name, self.office_id, self.is_active)

class ExamRoom(models.Model):
  room_id = models.IntegerField(default=-1)
  office = models.ForeignKey(Office, on_delete=models.CASCADE)

  def __unicode__(self):
    return 'exam room %s in office: %s, id %s' % (self.room_id, self.office.name, self.office.office_id)

class Patient(models.Model):
  name = models.CharField(max_length=200)
  doctor = models.ForeignKey(Doctor, default=None, on_delete=models.CASCADE)
  patient_id = models.IntegerField(default=0)
  date_of_birth = models.DateTimeField(default=datetime.datetime.now)
  email = models.EmailField(default=None)
  #add more fields

  def __unicode__(self):
    return '%s, %s' % (self.name, self.date_of_birth.date())


class Appointment(models.Model):
  appointment_id = models.CharField(default='', max_length=200)
  scheduled_time = models.DateTimeField()
  duration = models.IntegerField(default=0)
  doctor = models.ForeignKey(Doctor, default=None, on_delete=models.CASCADE)
  patient = models.ForeignKey(Patient, default=None, blank=True, null=True, on_delete=models.CASCADE)
  exam_room = models.ForeignKey(ExamRoom, default=None, blank=True, null=True, on_delete=models.CASCADE)
  office = models.ForeignKey(Office, on_delete=models.CASCADE)
  is_break = models.BooleanField(default=False)

  def __unicode__(self):
    if (self.is_break):
      return '%s, Break time' % self.scheduled_time
    else:
      return '%s, %s' % (self.scheduled_time, self.patient.name)
