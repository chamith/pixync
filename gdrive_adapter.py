#! /usr/bin/python3
# 
# # https://developers.google.com/drive/api/v3/quickstart/python
from __future__ import print_function
import os.path
from posixpath import relpath
from google.oauth2 import credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
import sys, glob, yaml
import xml.etree.ElementTree as ET
import metadata_util

# If modifying these scopes, delete the file token.json.
GOOGLE_API_SCOPES = ['https://www.googleapis.com/auth/drive']
GOOGLE_API_CLIENT_CRED_FILE = "gcp-client-secret.json"
GOOGLE_API_SERVICE_CRED_FILE = "gcp-service-key.json"
SCRIPT_DIR_PATH = os.path.dirname(os.path.realpath(__file__)) + os.path.sep
verbose = False
quiet = False
path_mappings = {}
local_repo_path = None

def get_dir(name, parent):
    candidates = gdrive_service.files().list(q="name='{}' and mimeType = 'application/vnd.google-apps.folder' and parents in '{}'".format(name, parent.get('id')), 
        spaces='drive', fields="nextPageToken, files(id, name)").execute()
    items = candidates.get('files', [])

    if len is None or len(items) == 0: 
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent.get('id')]
            }
        return gdrive_service.files().create(body=file_metadata,
                                    fields='id, name').execute()
    else:
        return items[0]

def get_dir_for_path(path, parent):
    global path_mappings

    for key in path_mappings:
        if key == path:
            return path_mappings[key]
    
    path = os.path.normpath(path)

    dir = parent
    for dir_comp in path.split(os.path.sep):
        dir = get_dir(dir_comp, dir)

    path_mappings[path] = dir
    return dir

def get_mime_type_by_ext(ext_mappings, ext):
    for k, v in ext_mappings.items():
        if k.lower() == ext.lower()[1:]: return v
    return 'application/octet-stream'
    
def get_files(local_repo_path, rating):
    files = []
    for file in metadata_util.get_metadata_files(local_repo_path):
        r = metadata_util.get_rating(file)
        if r >= rating:
            files.extend(metadata_util.get_related_files(file, local_repo_path))
    return files

def set_client_credentials(client_cred_file):
    global creds

    if not client_cred_file:
        client_cred_file = SCRIPT_DIR_PATH + GOOGLE_API_CLIENT_CRED_FILE
        
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', GOOGLE_API_SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_cred_file, GOOGLE_API_SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

def set_service_credentials(service_cred_file):
    global creds

    if not service_cred_file:
        service_cred_file = SCRIPT_DIR_PATH + GOOGLE_API_SERVICE_CRED_FILE

    creds = service_account.Credentials.from_service_account_file(
    service_cred_file, scopes=GOOGLE_API_SCOPES)

def set_config(config):
    global settings
    settings = config

def upload_to_gdrive(rating):
    global gdrive_service

    # settings = read_settings(settings_file)

    ext_mappings = {}
    for cat_key, cat_value in settings['gdrive-mime-type-mappings'].items():
        for ext in cat_value:
            ext_mappings[ext] = cat_key

    repo_name = os.path.split(local_repo_path.rstrip(os.path.sep))[1]

    files_to_upload = get_files(local_repo_path, rating)

    if verbose:
        print("repo to upload: ", repo_name) 
        print("rating >= ", rating)

    gdrive_service = build('drive', 'v3', credentials=creds)

    pixync_root_candidates = gdrive_service.files().list(q="name='pixync' and mimeType = 'application/vnd.google-apps.folder'", 
        spaces='drive', fields="nextPageToken, files(id, name)").execute()
    pixync_root = pixync_root_candidates.get('files', [])[0]

    for file in files_to_upload:

        dir_path, file_name = os.path.split(file)
        dir = get_dir_for_path(repo_name + '/' + dir_path, pixync_root)
        if verbose: print("GDrive Directory for the File: ", dir)

        existing_file_candidates = gdrive_service.files().list(q="name='{}' and parents in '{}'".format(file_name, dir.get('id')), 
            spaces='drive', fields="nextPageToken, files(id, name)").execute()
        items = existing_file_candidates.get('files', [])

        if len(items) == 0:
            if verbose: print("Uploading to GDrive ....")
            file_extension = os.path.splitext(file_name)[1]
            file_metadata = {
                'name': file_name,
                'parents': [dir.get('id')]
                }

            media = MediaFileUpload(local_repo_path + file, mimetype=get_mime_type_by_ext(ext_mappings, file_extension))
            new_file = gdrive_service.files().create(body=file_metadata,
                                                media_body=media,
                                                fields='id').execute()
            print ("File '{}' uploaded to GDrive ".format(file), end='')
            if verbose: print('[Id: {}]'.format(new_file.get('id')))
            else: print('')
        else:
            print("File '{}' already in GDrive ".format(file), end='')
            if verbose: print('[Id: {}]'.format(items[0].get('id')))
            else: print('')
