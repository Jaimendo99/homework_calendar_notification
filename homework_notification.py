import httpx
from icalendar import Calendar
from datetime import datetime, timedelta
import re
import json


# get time zone from local machine
def get_tz():
    now = datetime.now()
    local_now = now.astimezone()
    local_tz = local_now.tzinfo
    return local_tz


# get calendar events from brightspace ics
def get_cal_events(token):
    url = 'https://udla.brightspace.com/d2l/le/calendar/feed/user/feed.ics'
    querystring = {'token': token}
    homework = httpx.get(url, params=querystring)
    calendar = Calendar().from_ical(homework.text)
    return calendar


# parse calendar events into a dictoionary
def get_homework(calendar):
    today = datetime.today()
    time_delta = 7
    hws_json = {}
    for component in calendar.walk():
        if (component.name == "VEVENT") and (component.decoded("dtend") > datetime.now().astimezone()) and (
                component.decoded("dtend") < today.astimezone() + timedelta(days=time_delta)):
            homework = {}
            homework[str(component.get('UID'))] = {
                'COURSE': re.compile(r'(?<=-)(.*)(?=-)(.*)').findall(str(component.get("location")))[0][1][1:],
                'ASSIGMENT': str(component.get("summary")),
                'INIT_TIME': component.decoded('dtstart').astimezone(get_tz()),
                'END_TIME': component.decoded('dtend').astimezone(get_tz()),
                'DESCRIPTION': str(component.get("description")),
                'SEQUENCE': component.get("sequence"),
                'LAST-MODIFIED': component.get("last-modified").dt.astimezone(get_tz()),
                'DTSTAMP': component.get("dtstamp").dt.astimezone(get_tz()),
                'DL_TIME': component.decoded('dtend').astimezone(get_tz()) - datetime.now().astimezone(get_tz())
            }
            hws_json.update(homework)
    return hws_json


# send notification to pushbullet
def pushbullet_noti(title, body, TOKEN):
    msg = {
        "type": "note",
        "title": title, 
        "body": body
            }
    
    headers = {
        'Authorization': 'Bearer ' + TOKEN, 
        'Content-Type': 'application/json'
        }
    
    resp = httpx.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(msg), headers=headers)
    
    if resp.status_code != 200:
        raise Exception('Error', resp.status_code)
    else:
        print('Message sent')



# delete all pushbullet notifications
def deletePush(TOKEN):
    headers = {'Authorization': 'Bearer ' + TOKEN}
    try:
        httpx.delete('https://api.pushbullet.com/v2/pushes',
                    headers=headers, raise_for_status=True)
    except httpx.HTTPStatusError as exc:
        pushbullet_noti(exc, 'Error deleting push', TOKEN)
