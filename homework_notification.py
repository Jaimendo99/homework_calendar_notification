import httpx
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from email.message import EmailMessage
import ssl
import smtplib
import time
from config import cal_token, gmail_token, sender

def get_tz():
    now = datetime.now()
    local_now = now.astimezone()
    local_tz = local_now.tzinfo
    return local_tz


def get_cal_events(token):
    url = 'https://udla.brightspace.com/d2l/le/calendar/feed/user/feed.ics'
    querystring = {'token': token}
    homework = httpx.get(url, params=querystring)
    calendar = Calendar().from_ical(homework.text)
    return calendar


def get_homework(calendar):
    today = datetime.today()
    time_delta = 7
    hws_json = {}
    for index, component in enumerate(calendar.walk()):
        if (component.name == "VEVENT") and (component.decoded("dtend") > datetime.now().astimezone()) and (
                component.decoded("dtend") < today.astimezone() + timedelta(days=time_delta)):
            homework={}
            homework[component.get('UID')] = {
                'MATERIA': component.get("location"),
                'TAREA': component.get("summary"),
                'FECHA_INICIO': component.decoded('dtstart'),
                'FECHA_FINALIZACION': component.decoded('dtend'),
                'DESCRIPCION': component.get("description"),
                'SEQUENCE': component.get("sequence"),
                'LAST-MODIFIED': component.get("last-modified").dt,
                'DTSTAMP': component.get("dtstamp").dt,
                'CLASS': component.get("class")
            }
            hws_json.update(homework)