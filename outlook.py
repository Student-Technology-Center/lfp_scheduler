import requests
import uuid
import json
from datetime import datetime, date, time, timedelta

outlookApiEndpoint = 'https://outlook.office.com/api/v2.0{0}'

# Generic API call
def makeApiCall(method, url, token, userEmail, payload=None, params=None, headers=None, expected=requests.codes.ok):
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
		hdrs.update({'Content-Type':'application/json'})
		response = requests.patch(url, headers=hdrs, data=json.dumps(payload), params=params)
	elif (method.upper() == 'POST'):
		hdrs.update({'Content-Type':'application/json'})
		response = requests.post(url, headers=hdrs, data=json.dumps(payload), params=params)
	
	if (response.status_code == expected):
		return response.json()
	else:
		return None

def getMe(token):
	getMeUrl = outlookApiEndpoint.format('/me')

	queryParams = {'$select':'DisplayName,EmailAddress'}

	return makeApiCall('GET', getMeUrl, token, '', params=queryParams)

def getCalendars(data):
	url = outlookApiEndpoint.format('/me/calendars')
	return makeApiCall('GET', url, data.accessToken, data.user.email)

def getCalendarView(data):
	url = outlookApiEndpoint.format('/me/calendars/'+data.calendarId+'/calendarview')

	dayStart = datetime.combine(date.today(), time())

	dayEnd = dayStart + timedelta(hours=24)

	params = {'startDateTime':dayStart.isoformat(),
		'endDateTime':dayEnd.isoformat()}

	return makeApiCall('GET', url, data.accessToken, data.user.email, params=params, headers={'Prefer':'outlook.timezone="America/Los_Angeles"'})
	#res = makeApiCall('GET', url, token, email, params=params)

def createAppointment(data, name, startTime):
	url = outlookApiEndpoint.format('/me/calendars/'+data.calendarId+'/events')
	
	endTime = startTime + timedelta(hours=1)

	body = {
		'Subject':'LFP w/ '+name,
		'Body': {
			'ContentType':'HTML',
			'Content':'This confirms your appointment', },
		'Start': {
			'DateTime':startTime.isoformat(),
			#TODO: convert to UTC prior
			'TimeZone':'Pacific Standard Time', },
		'End': {
			'DateTime':endTime.isoformat(),
			'TimeZone':'Pacific Standard Time', },
	}

	return makeApiCall('POST', url, data.accessToken, data.user.email, payload=body, expected=requests.codes.created)

