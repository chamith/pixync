#! /usr/bin/python3
# 
# # https://developers.google.com/drive/api/v3/quickstart/python
from __future__ import print_function
from http.client import responses
import io
import os.path
from posixpath import relpath
from google.oauth2 import credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload
import sys, glob, yaml
import xml.etree.ElementTree as ET
import metadata_util

# If modifying these scopes, delete the file token.json.
GOOGLE_API_SCOPES = ['https://www.googleapis.com/auth/drive']
GOOGLE_API_CLIENT_CRED_FILE = "gcp-client-secret.json"
GOOGLE_API_SERVICE_CRED_FILE = "gcp-service-key.json"
SCRIPT_DIR_PATH = os.path.dirname(os.path.realpath(__file__)) + os.path.sep
TOKEN_FILE = ".pixync" + os.path.sep + "gcp-security-token.json"
verbose = False
quiet = False
path_mappings_repo_root = {}
path_mappings_repo_sub_dir = {}

local_repo_path = None
gdrive_repo_url = None
gdrive_tree = []

def print_step_header(title):
    if verbose: print("{:=^75}".format(title.upper()))

def print_step_footer():
    if verbose: print("{:=^75}".format(''))

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
        dir = items[0]


        return dir

def get_dir_for_path(path, parent, path_mappings):
    for key in path_mappings:
        if key == path:
            return path_mappings[key]
    
    path = os.path.normpath(path)

    dir = parent
    for dir_comp in path.split(os.path.sep):
        dir = get_dir(dir_comp, dir)

    path_mappings[path] = dir
    return dir

def get_available_file(file):
    dir_path, file_name = os.path.split(file)

    if dir_path in path_mappings_repo_sub_dir:
        dir = path_mappings_repo_sub_dir[dir_path]
        if 'files' in dir:
            for f in dir['files']:
                if f['name'] == file_name:
                    return f
            return None
        return None
    else:
        return None

def get_mime_type_by_ext(ext_mappings, ext):
    for k, v in ext_mappings.items():
        if k.lower() == ext.lower()[1:]: return v
    return 'application/octet-stream'

def get_local_files_with_ignored_ratings():
    files = []

    ignore_ratings = 'ignore-ratings'
    if not ignore_ratings in settings:
        return files

    for pattern in settings[ignore_ratings]:
        filter = local_repo_path + "/**/" + pattern
        for file in glob.iglob(filter, recursive=True):
            files.append(os.path.relpath(file, local_repo_path))

    return files

def get_local_files(local_repo_path, rating):
    files = []
    for file in metadata_util.get_metadata_files(local_repo_path):
        r = metadata_util.get_rating(file)
        if r >= rating:
            files.extend(metadata_util.get_related_files(file, local_repo_path))

    files.extend(get_local_files_with_ignored_ratings())

    return files

def set_client_credentials(client_cred_file):
    global creds

    if not client_cred_file:
        client_cred_file = SCRIPT_DIR_PATH + GOOGLE_API_CLIENT_CRED_FILE
        
    creds = None
    if os.path.exists(local_repo_path + TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(local_repo_path + TOKEN_FILE, GOOGLE_API_SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_cred_file, GOOGLE_API_SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(local_repo_path + TOKEN_FILE, 'w') as token:
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

def get_children_gdrive(parent, parent_path):
    print("> {}".format(parent_path if len(parent_path)>0 else '<root>'))
    if len(parent_path) > 0 and not os.path.exists(local_repo_path + os.path.sep + parent_path):
        os.makedirs(local_repo_path + os.path.sep + parent_path)

    children_response = gdrive_service.files().list(
        q="parents in '{}'".format(parent.get('id')), 
        spaces='drive', fields="nextPageToken, files(id, name, mimeType)").execute()
    children = children_response.get('files',[])
    for child in children:
        child_path = parent_path + os.path.sep + child['name'] if len(parent_path) > 0 else child['name']
        path_mappings_repo_sub_dir[child_path] = child
        if child['mimeType'] == 'application/vnd.google-apps.folder':
            get_children_gdrive(child, child_path)

def build_directory_tree_gdrive():
    print_step_header("building directory tree")
    get_children_gdrive(gdrive_repo_root, '')
    print_step_footer()

def download_files(rating):
    print_step_header("downloading files")
    for item in path_mappings_repo_sub_dir:
        local_file_path = local_repo_path + item
        local_file_rel_path = os.path.relpath(local_file_path, local_repo_path)
        if os.path.exists(local_file_path):
            print ('> {:<60}{:>13}'.format(local_file_rel_path, 'available'))
        else:
            request = gdrive_service.files().get_media(fileId=path_mappings_repo_sub_dir[item]['id'])
            fh = io.FileIO(item, 'wb')
            downloader = MediaIoBaseDownload(fh, request, chunksize=1024*1024)
            response = False
            while response is False:
                status, response = downloader.next_chunk()
                if status: print ('> {:<60}{:>13}'.format(local_file_rel_path, '[{}%]'.format(int(status.progress() * 100))), end='\r')
            print ('> {:<60}{:>13}'.format(local_file_rel_path,'downloaded'))
            
    print_step_footer()

def build_directory_tree_local():
    print_step_header('building directory tree')

    dir_tree = glob.glob(local_repo_path +'/**/', recursive=True)
    for dir_path in dir_tree:
        if dir_path == local_repo_path: continue
        gdrive_dir_path = os.path.relpath(dir_path, local_repo_path)
        if verbose: print('>' , gdrive_dir_path)
        dir = get_dir_for_path( gdrive_dir_path , gdrive_repo_root, path_mappings_repo_sub_dir)

        if not 'files' in dir:
            files_response = gdrive_service.files().list(q="mimeType != 'application/vnd.google-apps.folder' and parents in '{}'".format(dir.get('id')), 
            spaces='drive', fields="nextPageToken, files(id, name)").execute()
            files_in_dir = files_response.get('files',[])

            if verbose: 
                for file in files_in_dir: print(">> {}".format(file))

            dir['files'] = files_in_dir
    print_step_footer()

def upload_files(rating):
    ext_mappings = {}
    for cat_key, cat_value in settings['gdrive-mime-type-mappings'].items():
        for ext in cat_value:
            ext_mappings[ext] = cat_key


    print_step_header("uploading files")
    files_to_upload = get_local_files(local_repo_path, rating)

    for file in files_to_upload:
        dir_path, file_name = os.path.split(file)
        dir = get_dir_for_path(dir_path, gdrive_repo_root, path_mappings_repo_sub_dir)

        if get_available_file(file):
            print ('> {:<60}{:>13}'.format(file, 'available'))
        else:
            file_extension = os.path.splitext(file_name)[1]
            file_metadata = {
                'name': file_name,
                'parents': [dir.get('id')]
                }
            media = MediaIoBaseUpload(io.FileIO(local_repo_path + file),
                mimetype=get_mime_type_by_ext(ext_mappings, file_extension), chunksize=1024*1024, resumable=True)
            request = gdrive_service.files().create(body=file_metadata,
                    media_body=media,
                    fields='id, name')
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status: print ('> {:<60}{:>13}'.format(file, '[{}%]'.format(int(status.progress() * 100))), end='\r')
            dir['files'].append(response)
            print ('> {:<60}{:>13}'.format(file,'uploaded'))

    print_step_footer()

def init_gdrive_service():
    global gdrive_service, gdrive_pixync_root, gdrive_repo_path, gdrive_repo_root

    root_dir_id, gdrive_repo_path = gdrive_repo_url
    gdrive_service = build('drive', 'v3', credentials=creds)

    try:
        gdrive_pixync_root = gdrive_service.files().get(fileId=root_dir_id).execute()
        gdrive_repo_root = get_dir_for_path(gdrive_repo_path, gdrive_pixync_root, path_mappings_repo_root)

    except:
        print('Error occurred while accessing the pixync root directory on GDrive.')
        exit(1)

def upload_to_gdrive(rating):
    init_gdrive_service()
    build_directory_tree_local()
    upload_files(rating)

def pull(rating):
    init_gdrive_service()
    build_directory_tree_gdrive()
    download_files(rating)