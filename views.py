from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from lfp import authhelper

import time

@login_required
def home(request):
	#TODO: check if access token exists
	#TODO: render scheduler form here
	return HttpResponse(request.user.username)

	#redirectUri = request.build_absolute_uri(reverse('gettoken'))
	#signInUrl = authhelper.getSigninUrl(redirectUri)
	#return HttpResponseRedirect(signInUrl)

@login_required
def gettoken(request):
	authCode = request.GET['code']
	redirectUri = request.build_absolute_uri(reverse('gettoken'))
	token = authhelper.getTokenFromCode(authCode, redirectUri)
	accessToken = token['access_token']
	expireTime = int(time.time()) + token['expires_in'] - 300 # 5 minute buffer

	request.session['authenticated'] = True
	request.session['accessToken'] = accessToken
	request.session['refreshToken'] = token['refresh_token']
	request.session['expireTime'] = expireTime
	return HttpResponseRedirect(reverse('home'))

