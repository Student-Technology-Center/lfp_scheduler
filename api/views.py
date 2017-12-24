from lfp_scheduler.models import LfpAppointment

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime
import json

def time_to_str(time):
    return "t"

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
        calendar = LfpAppointment.objects().select_for_update()


        appt = LfpAppointment(
            start_time=datetime.now(),
            name=jsonRes['name'],
            prof=jsonRes['prof'],
            class_code=jsonRes['class_code'],
            email=jsonRes['email'],
            w_num=jsonRes['w_num'],
            priority=0,
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

    #TODO: Detect if data should be anonymized or not - just based on user authentication?
    jsonData = []
    for appt in LfpAppointment.objects.all():
        jsonData.append({'name':appt.name,
            'prof':appt.prof,
            'class_code':appt.class_code,
            'email':appt.email,
            'w_num':appt.w_num,
            'priority':appt.priority,
            'creator':appt.creator,
            'start_time':appt.start_time.isoformat(timespec='hours')})
    return JsonResponse({'status':'success', 'data':jsonData, 'message':'Requested calendar'})
