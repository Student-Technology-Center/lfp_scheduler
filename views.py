from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from lfp import authhelper
from lfp import outlook

import time
import datetime
import json

@login_required
def home(request):
	user = request.user
	userdata = request.user.userdata

	if (request.method == 'POST'):
		startTime = datetime.datetime.strptime(request.POST['begin_time'], '%Y-%m-%d %H:%M')
		outlook.createAppointment(userdata, request.POST['name'], startTime)
		
	else: # Assume request was GET
		authResult = authhelper.authorize(request)
		if authResult != None:
			return HttpResponseRedirect(authResult)
		#TODO: This should DEFINITELY not be done every reload... do only after full auth refresh?
		outlookMe = outlook.getMe(userdata.accessToken)
		if outlookMe['EmailAddress'] != user.email:
			print("Emails don't match! Replacing...")
			user.email = outlookMe['EmailAddress']
			user.save()

	calendars = outlook.getCalendars(userdata)

	# Find the proper calendar ID
	# TODO: Cache this for performance
	for item in calendars['value']:
		if (item['Name'] == 'test-calendar'):
			userdata.calendarId = item['Id']
			user.save()
	
	return render(request, 'lfp/form.html')

@login_required
def gettoken(request):
	authCode = request.GET['code']
	redirectUri = request.build_absolute_uri(reverse('gettoken'))
	token = authhelper.getTokenFromCode(authCode, redirectUri)
	if token == None:
		print("ERROR: Failed to get token from auth code!")
	authhelper.populateWithToken(request.user, token)

	return HttpResponseRedirect(reverse('home'))

