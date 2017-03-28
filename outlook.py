import requests
import uuid
import json
from datetime import datetime, date, time, timedelta

outlookApiEndpoint = 'https://outlook.office.com/api/v2.0{0}'

# Generic API call
def makeApiCall(method, url, token, userEmail, payload=None, params=None, headers=None):
	hdrs= {
		'X-AnchorMailbox':userEmail,
		'User-Agent':'LFP Scheduler/1.0',
		'Authorization':'Bearer {0}'.format(token),
		'Accept': 'application/json',
	}

	requestId = str(uuid.uuid4())
	instrumentation = {
		'client-request-id':requestId,
		'return-client-request-id':'true',
	}

	hdrs.update(instrumentation)
	if headers != None:
		hdrs.update(headers)

	response = None

	if (method.upper() == 'GET'):
		response = requests.get(url, headers=hdrs, params=params)
	elif (method.upper() == 'DELETE'):
		response = requests.delete(url, headers=hdrs, params=params)
	elif (method.upper() == 'PATCH'):
		headers.update({'Content-Type':'application/json'})
		response = requests.patch(url, headers=hdrs, data=json.dumps(payload), params=params)
	elif (method.upper() == 'POST'):
		headers.update({'Content-Type':'application/json'})
		response = requests.post(url, headers=hdrs, data=json.dumps(payload), params=params)
	
	return response

def getMe(token):
	getMeUrl = outlookApiEndpoint.format('/me')

	queryParams = {'$select':'DisplayName,EmailAddress'}

	res = makeApiCall('GET', getMeUrl, token, '', params=queryParams)
	if (res.status_code == requests.codes.ok):
		return res.json()
	else:
		return None

def getCalendars(token, email):
	url = outlookApiEndpoint.format('/me/calendars')
	res = makeApiCall('GET', url, token, email)

	if (res.status_code == requests.codes.ok):
		return res.json()
	else:
		return None

def getCalendarView(token, email, calendarId):
	url = outlookApiEndpoint.format('/me/calendars/'+calendarId+'/calendarview')

	dayStart = datetime.combine(date.today(), time())

	dayEnd = dayStart + timedelta(hours=24)

	params = {'startDateTime':dayStart.isoformat(),
		'endDateTime':dayEnd.isoformat()}

	res = makeApiCall('GET', url, token, email, params=params, headers={'Prefer':'outlook.timezone="America/Los_Angeles"'})
	#res = makeApiCall('GET', url, token, email, params=params)

	if (res.status_code == requests.codes.ok):
		return res.json()
	else:
		print("Error! statuscode: " + str(res.status_code))
		return None

