from pprint import pprint
from Google import Create_Service

CLIENT_SECRET= 'credentials.json'
API_NAME='calendar'
API_VERSION = 'v3'
SCOPES=['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/calendar.events.readonly','https://www.googleapis.com/auth/calendar.readonly','https://www.googleapis.com/auth/calendar.settings.readonly']

service =Create_Service(CLIENT_SECRET,API_NAME,API_VERSION,SCOPES)