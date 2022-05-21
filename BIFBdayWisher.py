from __future__ import print_function
import os.path
import requests
from datetime import date
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import creds as c

today = date.today()
d4 = today.strftime("%d-%m-%Y")

def SendMsg(bday):
    url = 'https://graph.facebook.com/v13.0/116141341097639/messages'
    jsondata = { "messaging_product": "whatsapp", "to": bday[0], "type": "template", "template": { "name": "bif_bdaywish", "language": { "code": "en_US" }, "components": [{"type":"body", "parameters":[{"type":"text", "text":bday[1]}] }] } }
    headers={'Authorization': c.WhatsappAuth}
    x = requests.post(url, headers=headers, json=jsondata)

def DataFromSheets():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    SPREADSHEET_ID = c.SheetID
    RANGE_NAME = 'A2:C3'


    
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=RANGE_NAME).execute()
        values = result.get('values', [])
        if not values:
            print('No data found.')
            return
        L=[]
        for row in values:
            if str(row[2])[:-6] == str(d4)[:-6]:
                L+=[[str(row[0]),row[1],row[2]]]
    except HttpError as err:
        print(err)
    return L

def main():
    L = DataFromSheets()
    if L != []:
        for i in L:
            SendMsg([i[0],i[1]])

main()