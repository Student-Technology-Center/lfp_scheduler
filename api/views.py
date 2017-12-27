from lfp_scheduler.models import LfpAppointment

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import dateparse

from datetime import datetime, time, timedelta
import json

# 0 = Monday, 1 = Friday, 2 = Saturday, 3 = Sunday
days = {0:[time(hour=8), time(hour=20)],
    1:[time(hour=8), time(hour=16)],
    2:[time(hour=11), time(hour=17)],
    3:[time(hour=14), time(hour=20)]}

#TODO: Handle holidays, changes of schedule
def datetime_valid(start_time):
    try:
        datetime_typed = dateparse.parse_datetime(start_time)
    except:
        return False
    time_portion = datetime_typed.time()
    week_index = datetime_typed.weekday() - 3
    week_index = 0 if week_index < 0 else week_index

    return days[week_index][0] <= time_portion and time_portion <= days[week_index][1]

@csrf_exempt
def lfp_api_event(request):
    if (request.method != 'POST' and request.method != 'DELETE'):
        return JsonResponse({'status':'error', 'message':'Invalid method! Must use POST or DELETE'}, status=405)

    if (request.method == 'POST'):
        try:
            jsonRes = json.loads(request.body)
        except:
            return JsonResponse({'status':'error', 'message':'Failed to parse JSON body!'}, status=400)

        #TODO: Verify, check for fill status
        calendar = LfpAppointment.objects.select_for_update()

        if not datetime_valid(jsonRes['start_time']) and not request.user.is_authenticated():
            return JsonResponse({'status':'error', 'message':'start time was invalid!'}, status=400)

        filled_slots = calendar.filter(start_time__exact=jsonRes['start_time']).count()
        if (filled_slots >= 4 and not request.user.is_authenticated()):
            return JsonResponse({'status':'error', 'message':'Appointment slot is already filled!'})

        #TODO: Sanitize
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

        return JsonResponse({'status':'success','message':'Created event!'})
    else: # Method is DELETE
        if (not request.user.is_authenticated()):
            return JsonResponse({'status':'error', 'message':'You must be logged in to delete an event!'}, status=401)
        return JsonResponse({'status':'success','message':'Deleted event!'})

@csrf_exempt
def lfp_api_calendar(request):
    if (request.method != 'GET'):
        return JsonResponse({'status':'error', 'message':'Invalid method! Must use GET'}, status=405)

    anonymize = True
    if (request.GET.get('full_data', '') == 'true'):
        if (not request.user.is_authenticated()):
            return JsonResponse({'status':'error', 'message':'You must be logged in to use full_data!'}, status=403)
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
    return JsonResponse({'status':'success', 'data':jsonData, 'message':'Requested calendar'})
