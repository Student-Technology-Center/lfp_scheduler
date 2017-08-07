from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from lfp_scheduler import authhelper
from lfp_scheduler import outlook
from lfp_scheduler.models import LfpData

import time
import datetime
import json

@login_required
def lfp(request):

    #user = request.user
    #userdata = request.user.userdata
    lfpdata = LfpData.load()

    authResult = authhelper.authorize(request)
    if authResult != None:
        print(authResult)
        return HttpResponseRedirect(authResult)

    if (request.method == 'POST'):
        startTime = datetime.datetime.strptime(request.POST['begin_time'], '%Y-%m-%d %H:%M')
        outlook.createAppointment(
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
    else: # Assume request was GET
        #TODO: This should DEFINITELY not be done every reload... do only after full auth refresh?
        #TODO: Check for return before dereferencing None
        outlookMe = outlook.getMe(lfpdata.accessToken)
        if outlookMe['EmailAddress'] != lfpdata.email:
            print("Emails don't match! Replacing...")
            lfpdata.email = outlookMe['EmailAddress']
            lfpdata.save()

    calendars = outlook.getCalendars(lfpdata)

    # Find the proper calendar ID
    # TODO: Cache this for performance
    for item in calendars['value']:
        print(item['Name'])
        if (item['Name'] == 'Large Format Printer'):
            print('id: ' + item['Id'])
            lfpdata.calendarId = item['Id']
            lfpdata.save()
    
    return render(request, 'form.html')

@login_required
def gettoken(request):
    authCode = request.GET['code']
    redirectUri = request.build_absolute_uri(reverse('gettoken'))
    token = authhelper.getTokenFromCode(authCode, redirectUri)
    if token == None:
        print("ERROR: Failed to get token from auth code!")
    authhelper.populateWithToken(LfpData.load(), token)

    return HttpResponseRedirect(reverse('lfp'))
