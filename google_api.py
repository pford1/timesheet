from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.http import MediaFileUpload
import os


def to_google_drive(file_name, google_drive_spred_sheet_name):

	# Setup the Sheets API
	SCOPES = [
		'https://www.googleapis.com/auth/drive'
		]
	store = file.Storage('credentials.json')
	creds = store.get()
	if not creds or creds.invalid:
	    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
	    creds = tools.run_flow(flow, store)
	service = build('drive', 'v3', http=creds.authorize(Http()))


	file_metadata = {
		'name' : google_drive_spred_sheet_name,
		'mimeType' : 'application/vnd.google-apps.spreadsheet',
		'parents' : []
	}

	media = MediaFileUpload(os.path.join(file_name), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', resumable=True)
	save_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()