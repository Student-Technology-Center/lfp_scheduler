from django.urls import reverse
from django.utils import timezone
from urllib.parse import quote, urlencode
import json
import time
from datetime import datetime, timedelta
import requests

from lfp_scheduler import lfp_pw
from lfp_scheduler.models import LfpData
from lfp_scheduler import outlook

# Client ID and secret - from lfp_password.py
client_id = lfp_pw.LFP_CLIENT_ID
client_secret = lfp_pw.LFP_CLIENT_SECRET

authority = 'https://login.microsoftonline.com'

authorize_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')

# The token issuing endpoint
token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')

# The scopes required by the app
scopes = [
    'openid',
    'email',
    'profile',
    'offline_access',
    'calendars.readwrite.shared',
    'mail.send',
    'user.read',
]

def buildSigninUrl(redirectUri):
    # Build the query parameters for the signin url
    params = { 'client_id': client_id,
             'redirect_uri': redirectUri,
             'response_type': 'code',
             'scope': ' '.join(str(i) for i in scopes),
             'state': '1337', # TODO: encode stuff in here
            }
    
    signin_url = authorize_url.format(urlencode(params))
    return signin_url

def getTokenFromCode(code, redirectUri):
    postData = { 'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirectUri,
        'scope': ' '.join(str(i) for i in scopes),
        'client_id': client_id,
        'client_secret': client_secret
        }
    result = requests.post(token_url, data = postData)

    if result.status_code != requests.codes.ok:
        print("getTokenFromCode returns {0} {1}".format(result.status_code, result.text))
        return None
    try:
        return result.json()
    except:
        return None

def saveToken(token):
    data = LfpData.load()
    data.accessToken = token['access_token']
    delta = token['expires_in']
    # Add extra 5 minute refresh buffer
    data.accessExpireTime = timezone.now() + timedelta(seconds=delta - 300)
    data.refreshToken = token['refresh_token']
    data.save()

def attemptRefresh(redirectUri):
    data = LfpData.load()

    signin = buildSigninUrl(redirectUri)

    if data.refreshToken == None:
        print("refresh token doesn't exist! Redirecting to microsoft...")
        return signin

    postData = { 'grant_type': 'refresh_token',
        'refresh_token': data.refreshToken,
        'redirect_uri': redirectUri,
        'scope': ' '.join(str(i) for i in scopes),
        'client_id': client_id,
        'client_secret': client_secret,
    }

    result = requests.post(token_url, data = postData)

    if result.status_code == requests.codes.ok:
        try:
            res = result.json()
            if (testApiCall(res['access_token'])):
                saveToken(res)
                return None
            else:
                return signin
        except:
            return signin
    else:
        return signin

# TODO: maybe move this to outlook?
def testApiCall(accessToken):
    if outlook.getMe(accessToken) == None:
        return False
    else:
        return True

# If function succeeds, return None, else return redirect uri
def authorize(request):
    print('authorizing...')

    data = LfpData.load()
    redirectUri = request.build_absolute_uri(reverse('gettoken'))

    if data.accessToken != None and data.accessExpireTime != None and datetime.now(timezone.utc) < data.accessExpireTime:
        if testApiCall(data.accessToken):
            print("Test api call succeeded, auth successful!")
            return None
        else:
            print("unexpired token existed, but API call failed, attempting refresh...")
            return attemptRefresh(redirectUri)
    else:
        print("Access token didn't exist or was expired, attempting refresh...")
        return attemptRefresh(redirectUri)
