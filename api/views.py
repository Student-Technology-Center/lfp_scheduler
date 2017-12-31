from lfp_scheduler.models import LfpAppointment

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import dateparse
from django.db.models import F

from datetime import datetime, time, timedelta
import json

# 0 = Monday, 1 = Friday, 2 = Saturday, 3 = Sunday
days = {0:[time(hour=8), time(hour=20)],
    1:[time(hour=8), time(hour=16)],
    2:[time(hour=11), time(hour=17)],
    3:[time(hour=14), time(hour=20)]}

#TODO: Handle holidays, changes of schedule
def start_time_valid(start_time):
    try:
        datetime_typed = dateparse.parse_datetime(start_time)
    except:
        return False
    time_portion = datetime_typed.time()
    week_index = datetime_typed.weekday() - 3
    week_index = 0 if week_index < 0 else week_index

    return days[week_index][0] <= time_portion and time_portion <= days[week_index][1]

def w_num_valid(w_num):
    return len(str(w_num)) <= 8

def construct_response(message, error=False, status=200, data=None):
    response = {'status':'error' if error else 'success', 'message':message}
    if data is not None:
        response.update({'data':data})
    return JsonResponse(response, status=status)

# TODO: Make sure each required JSON parameter exists

@csrf_exempt
def lfp_api_event(request):
    if (request.method != 'POST' and request.method != 'DELETE'):
        return construct_response('Invalid method! Must use POST or DELETE', error=True, status=405)

    calendar = LfpAppointment.objects.select_for_update()

    try:
        jsonRes = json.loads(request.body)
    except:
        return construct_response('Failed to parse JSON body!', error=True, status=400)

    if (request.method == 'POST'):
        if not start_time_valid(jsonRes['start_time']) and not request.user.is_authenticated():
            return construct_response('Start time was invalid!', error=True, status=400)

        if not w_num_valid(jsonRes['w_num']):
            return construct_response('Invalid W number!', error=True, status=400)

        filled_slots = calendar.filter(start_time__exact=jsonRes['start_time']).count()
        if (filled_slots >= 4 and not request.user.is_authenticated()):
            return construct_response('Appointment slot is already filled!', error=True, status=403)

        #TODO: Sanitize more
        appt = LfpAppointment(
            start_time=jsonRes['start_time'], 
            name=jsonRes['name'],
            prof=jsonRes['prof'],
            class_code=jsonRes['class_code'],
            email=jsonRes['email'],
            w_num=jsonRes['w_num'],
            priority=filled_slots + 1,
            creator=jsonRes['creator'])
        appt.save()

        return construct_response('Created event!')
    else: # Method is DELETE
        if (not request.user.is_authenticated()):
            return construct_response('You must be logged in to delete an event!', error=True, status=401)

        timeslot_events = calendar.filter(start_time__exact=jsonRes['start_time'])
        target_priority = timeslot_events.filter(priority__exact=jsonRes['priority'])

        if (target_priority.count() == 0):
            return construct_response('Couldn\'t find event with right priority and time!', error=True, status=404)

        target_priority.delete()

        # Lower priorities of events during same timeslot
        greater_priorities = timeslot_events.filter(priority__gt=jsonRes['priority'])
        greater_priorities.update(priority=F('priority') - 1)
        return construct_response('Deleted event!')

@csrf_exempt
def lfp_api_calendar(request):
    if (request.method != 'GET'):
        return construct_response('Invalid method! Must use GET', error=True, status=405)

    anonymize = True
    if (request.GET.get('show_full', '') == 'true'):
        if (not request.user.is_authenticated()):
            return construct_response('You must be logged in to use show_full!', error=True, status=403)
        anonymize = False

    jsonData = []
    for appt in LfpAppointment.objects.all():
        data = {'priority': appt.priority,
            'start_time':appt.start_time}
        if not anonymize:
            data.update({'name':appt.name,
                'prof':appt.prof,
                'class_code':appt.class_code,
                'email':appt.email,
                'w_num':appt.w_num,
                'creator':appt.creator})
        jsonData.append(data)
    return construct_response('Calendar request successful!', data=jsonData)
