from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404

from lfp_scheduler import authhelper
from lfp_scheduler import outlook
from lfp_scheduler.models import LfpData

import time
from datetime import datetime, timedelta
import json

#@login_required
def lfp(request):
    authResult = authhelper.authorize(request)
    if authResult != None:
        print("auth not complete, redirecting to {0}".format(authResult))
        return HttpResponseRedirect(authResult)

    authhelper.save_calendar_info()

    lfpdata = LfpData.load()

    if (request.method == 'POST'):
        startTime = datetime.strptime(request.POST['begin_time'], '%Y-%m-%d %H:%M')
        result = outlook.createAppointment(
            lfpdata,
            startTime,
            request.POST['client_name'],
            request.POST['client_prof'],
            request.POST['client_class'],
            request.POST['client_email'],
            request.POST['client_w_num'],
            request.POST['client_phone_num'],
            request.POST['priority'],
            request.POST['created_by'])
        if result == None:
            return render(request, 'form.html', {'status': 'Form failed to submit! Refresh to re-authenticate', 'postPrev': request.POST})
        else:
            return render(request, 'form.html', {'status': 'LFP was submitted successfully!'})

    #TODO: This should DEFINITELY not be done every reload... do only after full auth refresh?
    #TODO: Check for return before dereferencing None
    #outlookMe = outlook.getMe(lfpdata.accessToken)
    #if outlookMe == None:
    #    print("API call failed!")
    #else:
    #    print(outlookMe)
    #    if lfpdata.email == None or outlookMe['mail'] != lfpdata.email:
    #        print("Emails don't match! Replacing...")
    #        lfpdata.email = outlookMe['mail']
    #        lfpdata.save()

    #calendars = outlook.getCalendars(lfpdata)

    # Find the proper calendar ID
    # TODO: Cache this for performance
    #for item in calendars['value']:
    #    print(item)
    #    if (item['name'] == 'Large Format Printer'):
    #        print('id: ' + item['id'])
    #        lfpdata.calendarId = item['id']
    #        lfpdata.save()
    
    return render(request, 'form.html')

def lfp_public(request):
    return render(request, "lfp.html");

#@login_required
def gettoken(request):
    # TODO: Check request.GET['state']
    authCode = request.GET['code']
    redirectUri = request.build_absolute_uri(reverse('gettoken'))
    token = authhelper.getTokenFromCode(authCode, redirectUri)
    if token == None:
        print("ERROR: Failed to get token from auth code!")
        raise Http404("Failed to get auth token!")
    else:
        authhelper.saveToken(token)
        authhelper.save_calendar_info()

    return HttpResponseRedirect(request.build_absolute_uri(reverse('lfp_public')))

