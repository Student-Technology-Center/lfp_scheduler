from django.urls import reverse
from django.utils import timezone
from urllib.parse import quote, urlencode
import json
import time
from datetime import datetime, timedelta
import requests
from lfp_scheduler import lfp_pw

# Client ID and secret - from lfp_password.py
client_id = lfp_pw.LFP_CLIENT_ID
client_secret = lfp_pw.LFP_CLIENT_SECRET

authority = 'https://login.microsoftonline.com'

authorize_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')

# The token issuing endpoint
token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')

# The scopes required by the app
scopes = ['openid',
		'offline_access',
		'https://outlook.office.com/calendars.readwrite.shared',
		]

def getSigninUrl(redirectUri):
	# Build the query parameters for the signin url
	params = { 'client_id': client_id,
			 'redirect_uri': redirectUri,
			 'response_type': 'code',
			 'scope': ' '.join(str(i) for i in scopes)
			}
	
	signin_url = authorize_url.format(urlencode(params))
	return signin_url

def getTokenFromCode(authCode, redirectUri):
	postData = { 'grant_type': 'authorization_code',
		'code': authCode,
		'redirect_uri': redirectUri,
		'scope': ' '.join(str(i) for i in scopes),
		'client_id': client_id,
		'client_secret': client_secret
		}
	result = requests.post(token_url, data = postData)

	if result.status_code != requests.codes.ok:
		return None
	try:
		return result.json()
	except:
		return None

def getTokenFromRefresh(refreshToken, redirectUri):
	postData = { 'grant_type': 'refresh_token',
		'refresh_token': refreshToken,
		'redirect_uri': redirectUri,
		'scope': ' '.join(str(i) for i in scopes),
		'client_id': client_id,
		'client_secret': client_secret,
	}

	result = requests.post(token_url, data = postData)

	if (result.status_code != requests.codes.ok):
		return None
	try:
		return result.json()
	except:
		return None

def populateWithToken(lfpdata, token):
	lfpdata.accessToken = token['access_token']
	delta = token['expires_in']
	# Add extra 5 minute refresh buffer
	lfpdata.accessExpireTime = timezone.now() + timedelta(seconds=delta - 300)
	lfpdata.refreshToken = token['refresh_token']
	lfpdata.save()

# If function succeeds, return None, else return redirect uri
def authorize(request):
	print('authorizing...')
	data = LfpData.load()
	if data.accessToken != None and data.accessExpireTime != None and datetime.now(timezone.utc) < data.accessExpireTime:
		# TODO: make a test API call
		print('expire time: '+str(data.accessExpireTime)+' current time: '+str(timezone.now()))
		return None
	elif data.refreshToken != None:
		print("Refreshing access for user "+request.user.username+" with refresh token!")
		token = getTokenFromRefresh(data.refreshToken, request.build_absolute_uri(reverse('gettoken')))
		if (token == None): # Refresh code might be expired
			data.accessToken = None
			data.accessExpireTime = None
			data.refreshToken = None
			data.save()
			return request.build_absolute_uri(reverse('home'))
		else:
			populateWithToken(request.user, token)
			return None
	else:
		# Go through the auth process from the beginning
		print("Refresh token doesnt' exist! Going through auth process...")
		redirectUri = request.build_absolute_uri(reverse('gettoken'))
		return getSigninUrl(redirectUri)

