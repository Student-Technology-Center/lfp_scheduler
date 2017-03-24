from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from lfp import authhelper

import time

@login_required
def home(request):
	#TODO: check if access token exists
	authResult = authhelper.authorize(request)
	if authResult != None:
		return HttpResponseRedirect(authResult)
	#TODO: render scheduler form here
	return HttpResponse(request.user.username + " " + request.user.userdata.accessToken)

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

