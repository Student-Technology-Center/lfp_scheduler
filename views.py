from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from lfp_scheduler import authhelper
from lfp_scheduler import outlook

import time
import datetime
import json

@login_required
def lfp(request):
	user = request.user
	userdata = request.user.userdata

	authResult = authhelper.authorize(request)
	if authResult != None:
		return HttpResponseRedirect(authResult)

	if (request.method == 'POST'):
		startTime = datetime.datetime.strptime(request.POST['begin_time'], '%Y-%m-%d %H:%M')
		outlook.createAppointment(
			userdata,
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
		outlookMe = outlook.getMe(userdata.accessToken)
		if outlookMe['EmailAddress'] != user.email:
			print("Emails don't match! Replacing...")
			user.email = outlookMe['EmailAddress']
			user.save()

	calendars = outlook.getCalendars(userdata)

	# Find the proper calendar ID
	# TODO: Cache this for performance
	for item in calendars['value']:
		print(item['Name'])
		if (item['Name'] == 'Large Format Printer'):
			print('id: ' + item['Id'])
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
