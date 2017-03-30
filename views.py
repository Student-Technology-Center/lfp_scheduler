from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from lfp import authhelper
from lfp import outlook

import time
import json

@login_required
def home(request):
	if (request.method == 'POST'):
		print('received post')
		#TODO: Sanitize and submit form input here
	
	user = request.user
	userdata = request.user.userdata
	authResult = authhelper.authorize(request)
	if authResult != None:
		return HttpResponseRedirect(authResult)

	#TODO: This should DEFINITELY not be done every reload... do only after full auth refresh?
	outlookMe = outlook.getMe(userdata.accessToken)
	if outlookMe['EmailAddress'] != user.email:
		print("Emails don't match! Replacing...")
		user.email = outlookMe['EmailAddress']
		user.save()
	
	calendars = outlook.getCalendars(userdata.accessToken, user.email)

	# Find the proper calendar ID
	# TODO: Cache this for performance
	calendarId = ''
	for item in calendars['value']:
		if (item['Name'] == 'test-calendar'):
			calendarId = item['Id']
	
	calendarView = outlook.getCalendarView(userdata.accessToken, user.email, calendarId)

	#for item in calendarView['value']:

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

