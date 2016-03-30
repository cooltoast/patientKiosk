from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import datetime, pytz, requests

from .models import Doctor, Patient, Appointment

BASE_URL = 'https://drchrono.com'

scope = 'patients:read patients:write calendar:read calendar:write clinical:read clinical:write'

def getHeader(access_token):
  return {
    'Authorization': 'Bearer %s' % access_token
  }

# retrieve and save todays appointments and update perninent patients
def getTodaysAppointments(doctor):
  appointments = [] 
  
  url = '%s/api/appointments' % BASE_URL
  params = {
    'doctor':doctor.doctor_id,
    'date':datetime.datetime.now().isoformat()
  }
  while url:
    data = requests.get(url, params=params, headers=getHeader(doctor.access_token)).json()
    appointments.extend(data['results'])
    url = data['next'] # A JSON null on the last page

  for appointment in appointments:
    patient_id = appointment['patient']
    patient = None
    is_break = True

    # update patient's info if appointment is not break
    if patient_id is not None:
      is_break = False

      patient_url = '%s/api/patients/%s' % (BASE_URL, patient_id)
      data = requests.get(patient_url, headers=getHeader(doctor.access_token)).json()

      full_name = data['first_name'] + ' ' + data['last_name']
      dobString = data['date_of_birth'].replace('-','')
      dob = datetime.datetime.strptime(dobString,'%Y%m%d')
      timezoneAwareDob = pytz.timezone('America/Los_Angeles').localize(dob)

      # update Patient if exists or create new
      params = {
        'name':full_name,
        'doctor':doctor,
        'email':data['email'],
        'date_of_birth':timezoneAwareDob,
        'patient_id':patient_id,
        # etc
      }
      patient, patientCreated = Patient.objects.update_or_create(
        patient_id=patient_id,
        defaults=params
      )

      if patientCreated:
        print 'created patient: %s' % params


    duration = int(appointment['duration'])
    start_time_iso = appointment['scheduled_time']
    start_time = datetime.datetime.strptime(start_time_iso, "%Y-%m-%dT%H:%M:%S")
    timezoneAwareStartTime = pytz.timezone('America/Los_Angeles').localize(start_time)
    timezoneAwareEndTime = timezoneAwareStartTime + datetime.timedelta(minutes=duration)

    # update Appointment if exists or create new
    params = {
      'start_time':timezoneAwareStartTime,
      'end_time':timezoneAwareEndTime,
      'doctor':doctor,
      'patient':patient,
      'is_break':is_break
    }
    appointment, appointmentCreated = Appointment.objects.update_or_create(
      defaults=params,
      **params
    )

# Create your views here.
def login(request):
    return render(request, 'kiosk/login.html', {'redirect_uri':settings.REDIRECT_URI, 'client_id':settings.CLIENT_ID, 'scope':scope})

def login_redirect(request):
    error = request.GET.get('error')
    if (error is not None):
        raise ValueError('Error authorizing application: %s' % error)

    response = requests.post('%s/o/token/' % BASE_URL, data={
        'code': request.GET.get('code'),
        'grant_type': 'authorization_code',
        'redirect_uri': settings.REDIRECT_URI,
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET
    })
    response.raise_for_status()
    data = response.json()

    access_token = data['access_token']
    refresh_token = data['refresh_token']
    expires_timestamp = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=data['expires_in'])

    response = requests.get('%s/api/users/current' % BASE_URL, headers=getHeader(access_token))
    response.raise_for_status()
    data = response.json()

    doctor_id = data['doctor']
    username = data['username']

    # update Doctor if exists or create new
    params = {
      'name':username,
      'doctor_id':doctor_id,
      'access_token':access_token,
      'refresh_token':refresh_token,
      'expires_timestamp':expires_timestamp
    }
    doctor, doctorCreated = Doctor.objects.update_or_create(
      doctor_id=doctor_id,
      defaults=params
    )

    # get appointments for today /appointments
    getTodaysAppointments(doctor)

    return render(request, 'kiosk/login_redirect.html', {'doctor':username, 'doctor_created':doctorCreated}) #patients:createdPatients


'''
def updatePatientList(doctor):
  patients = []
  createdPatients = []
  # get /api/patients to retrieve email
  patients_url = '%s/api/patients' % BASE_URL
  while patients_url:
    data = requests.get(patients_url, headers=getHeader(doctor.access_token)).json()
    patients.extend(data['results'])
    patients_url = data['next'] # A JSON null on the last page

  for patient in patients:
    full_name = patient['first_name'] + ' ' + patient['last_name']
    dobString = patient['date_of_birth'].replace('-','')
    dob = datetime.datetime.strptime(dobString,'%Y%m%d')
    timezoneAwareDob = pytz.timezone('America/Los_Angeles').localize(dob)
    patient_id = patient['id']

    # update if exists or create new
    params = {
      'name':full_name,
      'email':patient['email'],
      'date_of_birth':timezoneAwareDob,
      'patient_id':patient_id,
      'doctor':doctor,
    }
    p, patientCreated = Patient.objects.update_or_create(
      patient_id=patient_id,
      defaults=params
    )

    if patientCreated:
      # only add important info
      createdPatients.append(params)

  return createdPatients
'''
