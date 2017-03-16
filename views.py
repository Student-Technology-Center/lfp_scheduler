from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from lfp import authhelper
import time

def home(request):
	return HttpResponse('home')

def login(request):
	redirectUri = request.build_absolute_uri(reverse('gettoken'))
	signInUrl = authhelper.getSigninUrl(redirectUri)
	return HttpResponse('<a href="' + signInUrl + '">Click here to sign in</a>')

def gettoken(request):
	authCode = request.GET['code']
	redirectUri = request.build_absolute_uri(reverse('gettoken'))
	token = authhelper.getTokenFromCode(authCode, redirectUri)
	print('http result: ', token)
	accessToken = token['access_token']
	expireTime = int(time.time()) + token['expires_in'] - 300 # 5 minute buffer

	request.session['accessToken'] = accessToken;
	request.session['refreshToken'] = token['refresh_token']
	request.session['expireTime'] = expireTime;
	return HttpResponseRedirect(reverse('home'))

