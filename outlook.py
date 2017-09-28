import requests
import uuid
import json
from datetime import datetime, date, time, timedelta

#graphEndpoint = 'https://outlook.office.com/api/v2.0{0}'
graphEndpoint = 'https://graph.microsoft.com/v1.0{0}'
stcUser = '/users/StudentTechnology.Center@wwu.edu'

# Generic API call
def makeApiCall(method, url, token, userEmail, payload=None, params=None, headers=None, expected=[requests.codes.ok]):
    hdrs= {
        'User-Agent':'lfp_scheduler/1.0',
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
    
    if (response.status_code in expected):
        return response.json()
    else:
        print("api call failed with code: " + str(response.status_code))
        print("dump:\n"+response.text+"\nend dump\n")
        return None

def getMe(token):
    getMeUrl = graphEndpoint.format('/me')

    queryParams = {'$select': 'displayName,mail'}

    return makeApiCall('GET', getMeUrl, token, '', params=queryParams)

def getCalendars(data):
    url = graphEndpoint.format(stcUser + '/calendars')
    return makeApiCall('GET', url, data.accessToken, data.email)

def getCalendarView(data):
    url = graphEndpoint.format(stcUser + '/'+data.calendarId+'/calendarview')

    dayStart = datetime.combine(date.today(), time())

    dayEnd = dayStart + timedelta(hours=24)

    params = {'startDateTime':dayStart.isoformat(),
        'endDateTime':dayEnd.isoformat()}

    return makeApiCall('GET', url, data.accessToken, data.email, params=params, headers={'Prefer':'outlook.timezone="America/Los_Angeles"'})
    #res = makeApiCall('GET', url, token, email, params=params)

BODY_STR = ("<br>This confirms your appointment on {0} at {1} at the "+
"Student Technology Center. If you are unable to keep this appointment, "+
"please reply to let us know or call 360-650-4300. The largest you can "+
"print is 30x40 inches. Please bring it in PDF or PowerPoint format on "+
"a flash drive.<br><br>Thanks!<br>"+
"________________________________<br><br>"+
"Client Name: {2}<br>Professor/Instructor: {3}<br>"+
"Class: {4}<br>WWU e-mail: {5}<br>"+
"W#: {6}<br>Contact Phone: {7}<br>"+
"Priority: {8}<br>Appointment made by: {9}<br>")

def createAppointment(data, startTime, name, prof, classCode, email, wNum, phone, priority, creator):
    url = graphEndpoint.format(stcUser + '/calendars/' + data.calendarId+'/events')
    
    endTime = startTime + timedelta(hours=1)

    body = {
        'subject':'LFP w/ '+name.split()[0],
        'body': {
            'contentType':'HTML',
            'content':BODY_STR.format(str(startTime.month)+'/'+str(startTime.day),
                startTime.strftime('%I:%M %p'),
                name,
                prof,
                classCode,
                email,
                wNum,
                phone,
                priority,
                creator)},
        'start': {
            'DateTime':startTime.isoformat(),
            #TODO: convert to UTC prior
            'TimeZone':'Pacific Standard Time', },
        'end': {
            'DateTime':endTime.isoformat(),
            'TimeZone':'Pacific Standard Time', },
        'attendees': [{
            'emailAddress': {
                'address':email,
                'name':name
            },
            'type':'Optional'
        }]
    }

    return makeApiCall('POST', url, data.accessToken, data.email, payload=body, expected=[requests.codes.created])

