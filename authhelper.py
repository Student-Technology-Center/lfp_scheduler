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

# Get access token from auth code returned by gettoken redirect
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

# Save access token into model
def saveToken(token):
    data = LfpData.load()
    data.accessToken = token['access_token']
    delta = token['expires_in']
    # Subtract 5 minute for refresh buffer
    data.accessExpireTime = datetime.now(timezone.utc) + timedelta(seconds=delta - 300)
    data.refreshToken = token['refresh_token']
    data.save()

def save_calendar_info():
    data = LfpData.load()
    me = outlook.getMe(data.accessToken)
    if me is None:
        return False
    data.email = me['mail']
    data.save()
    cid = outlook.getLfpCalendar(data)
    if cid is None:
        return False
    data.calendarId = cid['id']
    data.save()
    return True


# Attempts to refresh access token from refresh token
# in lfp model - returns None on success,
# otherwise returns redirect uri for required sign-in
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
    return outlook.getMe(accessToken) != None

def time_remaining(data):
    return (data.accessToken is not None and
            data.accessExpireTime is not None and
            datetime.now(timezone.utc) < data.accessExpireTime)

def should_authorize(data):
    return (time_remaining(data) and
            data.email is not None and
            data.calendarId is not None)

# If function succeeds, return None, else return redirect uri
def authorize(request):
    print('authorizing...')

    data = LfpData.load()
    redirectUri = request.build_absolute_uri(reverse('gettoken'))

    # Check if access token exists and is up-to-date
    if time_remaining(data):
        # Attempt to repopulate calendar and email
        if save_calendar_info():
            return None
        else:
            print("unexpired token existed, but API call failed, attempting refresh...")
    else:
        print("Access token didn't exist or was expired, attempting refresh...")

    res = attemptRefresh(redirectUri)
    if res is None:
        if not save_calendar_info():
            print("Something is really bad!!! Auth succeeded, but getting calendar ID failed")
    return res

