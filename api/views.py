from lfp_scheduler.models import LfpData
from lfp_scheduler import outlook, authhelper

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import dateparse
from django.db.models import F

from datetime import datetime, date, time, timedelta
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

# Response structure:
# { 'status':'error' or 'success',
# 'message': 'status'
# 'data': Specific to command, optional
def construct_response(message, error=False, status=200, data=None):
    response = {'status':'error' if error else 'success', 'message':message}
    if data is not None:
        response.update({'data':data})
    return JsonResponse(response, status=status)

@csrf_exempt
def lfp_api_event(request):
    if (request.method != 'POST' and request.method != 'DELETE'):
        return construct_response('Invalid method! Must use POST or DELETE', error=True, status=405)

    if (request.method == 'POST'):
        return construct_response('Created event!')
    else: # Method is DELETE
        return construct_response('You must be logged in to delete an event!', error=True, status=401)

@csrf_exempt
def lfp_api_calendar(request):
    if (request.method != 'GET'):
        return construct_response('Invalid method! Must use GET', error=True, status=405)

    lfp_data = LfpData.load()

    # TODO: Get this from request somehow
    startDay = datetime.combine(date.today(), time())
    endDay = startDay + timedelta(hours=72)

    if not authhelper.should_authorize(lfp_data):
        res = authhelper.authorize(request)
        if res is not None:
            return construct_response("Refresh required: {}".format(res), error=True)
        lfp_data = LfpData.load()

    events = outlook.getCalendarView(lfp_data, startDay.isoformat(), endDay.isoformat())
    ret_obj = []
    if events is not None and 'value' in events.keys(): # TODO: Check actual body for error
        for e in events['value']:
            ret_obj.append({'start_time':e['start']['dateTime']})
    else:
        pass

    return construct_response("Fetched events",data=ret_obj)

