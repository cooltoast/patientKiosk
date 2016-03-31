from django.contrib import admin

from .models import Doctor, Patient, Appointment, Office, ExamRoom
# Register your models here.

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Office)
admin.site.register(ExamRoom)
