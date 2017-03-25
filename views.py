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
	user = request.user
	userdata = request.user.userdata
	authResult = authhelper.authorize(request)
	if authResult != None:
		return HttpResponseRedirect(authResult)

	outlookMe = outlook.getMe(userdata.accessToken)
	if outlookMe['EmailAddress'] != user.email:
		print("Emails don't match! Replacing...")
		user.email = outlookMe['EmailAddress']
		user.save()
	
	calendars = outlook.getCalendars(userdata.accessToken, user.email)

	# Find the proper calendar ID
	calendarId = ''
	for item in calendars['value']:
		if (item['Name'] == 'test-calendar'):
			calendarId = item['Id']
	
	calendarView = outlook.getCalendarView(userdata.accessToken, user.email, calendarId)

	return HttpResponse(json.dumps(calendarView))
	#return HttpResponse(outlookMe['DisplayName']+'\n'+user.username + " " +userdata.accessToken+'\n'+str(userdata.accessExpireTime))

	#redirectUri = request.build_absolute_uri(reverse('gettoken'))
	#signInUrl = authhelper.getSigninUrl(redirectUri)
	#return HttpResponseRedirect(signInUrl)

@login_required
def gettoken(request):
	authCode = request.GET['code']
	redirectUri = request.build_absolute_uri(reverse('gettoken'))
	token = authhelper.getTokenFromCode(authCode, redirectUri)
	if token == None:
		print("ERROR: Failed to get token from auth code!")
	authhelper.populateWithToken(request.user, token)

	return HttpResponseRedirect(reverse('home'))

