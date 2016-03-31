from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import datetime, pytz, requests

from .models import Doctor, Patient, Appointment, Office, ExamRoom
from .forms import AppointmentForm, OfficeForm

BASE_URL = 'https://drchrono.com'

scope = 'patients:read patients:write calendar:read calendar:write clinical:read clinical:write user:read user:write'

from .forms import NewAppointmentForm
from django.views.generic.edit import FormView

class NewAppointmentFormView(FormView):
    template_name = 'kiosk/new_appt.html'
    form_class = NewAppointmentForm
    success_url = '/kiosk/new_appt'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        formData = form.cleaned_data
        doctor = formData['doctor']
        examRoom = formData['exam_room']
        office = formData['office']
        patient = formData['patient']
        params = {
            'doctor':doctor.doctor_id,
            'duration':formData['duration'],
            'exam_room':examRoom.room_id,
            'office':office.office_id,
            'patient':patient.patient_id,
            'scheduled_time':datetime.datetime.combine(datetime.date.today(), formData['scheduled_time']),
            'status':'Arrived'
        }
        url = '%s/api/appointments' % BASE_URL

        response = requests.post(url, headers=getHeader(doctor.access_token), data=params)
        response.raise_for_status()
        data = response.json()

        # form.create_appt()

        # update Appointment if exists or create new
        params['appointment_id'] = data['id']
        params['doctor'] = doctor
        params['exam_room'] = examRoom
        params['office'] = office
        params['patient'] = patient

        appointment, appointmentCreated = Appointment.objects.update_or_create(
          appointment_id=params['appointment_id'],
          defaults=params
        )

        if appointmentCreated:
          print 'created appointment: %s' % appointment

        return super(NewAppointmentFormView, self).form_valid(form)


def getHeader(access_token):
  return {
    'Authorization': 'Bearer %s' % access_token
  }

# retrieve and save todays appointments and update perninent patients
def getTodaysAppointments(doctor):

  appointments = [] 
  
  activeOffice = Office.objects.get(is_active=True)
  url = '%s/api/appointments' % BASE_URL
  params = {
    'doctor':doctor.doctor_id,
    'office':activeOffice.office_id,
    'date':datetime.datetime.now().isoformat()
  }
  while url:
    data = requests.get(url, params=params, headers=getHeader(doctor.access_token)).json()
    appointments.extend(data['results'])
    url = data['next'] # A JSON null on the last page

  for appointment in appointments:
    appointment_id = appointment['id']
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
      timezoneAwareDob = pytz.utc.localize(dob)

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
    scheduled_time_iso = appointment['scheduled_time']
    scheduled_time = datetime.datetime.strptime(scheduled_time_iso, "%Y-%m-%dT%H:%M:%S")
    timezoneAwareScheduledTime = pytz.utc.localize(scheduled_time)

    examRoom = None
    if not is_break:
      examRoom = activeOffice.examroom_set.get(room_id=appointment['exam_room'])

    # update Appointment if exists or create new
    params = {
      'appointment_id':appointment_id,
      'scheduled_time':timezoneAwareScheduledTime,
      'duration':duration,
      'doctor':doctor,
      'patient':patient,
      'exam_room':examRoom,
      'office':activeOffice,
      'is_break':is_break
    }
    appointment, appointmentCreated = Appointment.objects.update_or_create(
      defaults=params,
      **params
    )

# Create your views here.
def login(request):
    return render(request, 'kiosk/login.html', {'redirect_uri':settings.REDIRECT_URI, 'client_id':settings.CLIENT_ID, 'scope':scope})

def new_appt(request):
    return render(request, 'kiosk/new_appt.html')

def set_office(request):
    template = 'kiosk/set_office.html'
    if request.method == 'POST':
        form = OfficeForm(request.POST)
        if form.is_valid():
            office = form.cleaned_data['office']
            office.is_active = True
            office.save()
            Office.objects.exclude(office_id=office.office_id).update(is_active=False)

            return render(request, template, {'form': OfficeForm(), 'message':'Successfully checked in for office: %s!' % office.name})

    else:
        form = OfficeForm()

    return render(request, template, {'form': form})


def checkin(request):
    template = 'kiosk/checkin.html'
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            appt = form.cleaned_data['appointment']
            url = '%s/api/appointments/%s' % (BASE_URL, appt.appointment_id)

            response = requests.patch(url, headers=getHeader(appt.doctor.access_token), data={'status':"Arrived"})
            response.raise_for_status()
            data = response.json()

            return render(request, template, {'form': AppointmentForm(), 'message':'Successfully checked in for %s!' % appt.patient.name})

    else:
        form = AppointmentForm()
        getTodaysAppointments(Doctor.objects.all()[0])

    return render(request, template, {'form': form})

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

    offices = []

    url = '%s/api/offices' % BASE_URL
    while url:
      data = requests.get(url, headers=getHeader(doctor.access_token)).json()
      offices.extend(data['results'])
      url = data['next'] # A JSON null on the last page

    for officeDict in offices:
      office_id = officeDict['id']
      params = {
        'name':officeDict['name'],
        'office_id':office_id,
        'doctor':doctor
      }
      office, officeCreated = Office.objects.update_or_create(
        office_id=office_id,
        defaults=params
      )

      for exam_room in officeDict['exam_rooms']:
        params = {
          'room_id':exam_room['index'],
          'office':office
        }
        e, roomCreated = ExamRoom.objects.update_or_create(
          defaults=params,
          **params
        )

    return render(request, 'kiosk/login_redirect.html', {'doctor':username, 'offices':offices})


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
