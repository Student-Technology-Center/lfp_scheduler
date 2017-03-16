from urllib.parse import quote, urlencode
import json
import time
import requests
import lfp_password

# Client ID and secret
client_id = LFP_CLIENT_ID
client_secret = LFP_CLIENT_SECRET

authority = 'https://login.microsoftonline.com'

authorize_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')

# The token issuing endpoint
token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')

# The scopes required by the app
scopes = ['openid',
		'offline_access',
		'https://outlook.office.com/mail.read',
		'https://outlook.office.com/calendars.readwrite.shared',
		'https://outlook.office.com/mail.send',
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
	r = requests.post(token_url, data = postData)

	try:
		return r.json()
	except:
		return 'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)

def getTokenFromRefresh(refreshToken, redirectUri):
	postData = { 'grant_type': 'refresh_token',
		'refresh_token': refreshToken,
		'redirect_uri': redirectUri,
		'scope': ' '.join(str(i) for i in scopes),
		'client_id': clientId,
		'client_secret': clientSecret,
	}

	result = requests.post(token_url, data = postData)

	try:
		return result.json();
	except:
		return 'Error retrieving token from refresh: {0} - {1}'.format(result.status_code, result.text)

def getAccessToken(request, redirectUri):
	currentToken = request.session['access_token']
	expireTime = request.session['expire_time']
	currentTime = int(time.time())
	if (currentToken and currentTime < expireTime):
		return currentToken
	else:
		refreshToken = request.session['refresh_token']
		newTokens = getTokenFromRefresh(refreshToken, redirectUri)

		request.session['access_token'] = newTokens['access_token']
		request.session['refresh_token'] = newTokens['refresh_token']
		request.session['expire_time'] = int(time.time()) + newTokens['expires_in'] - 300
		
		return newToken['access_token']

