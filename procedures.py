#! /bin/python3

from posixpath import sep
import sys
import getopt
import subprocess
import yaml
import os
import glob
import platform
from pathlib import Path
import time
CONFIG_FILE_NAME = ".pixync"
IGNORE_FILE_NAME = ".pixignore"
SETTINGS_FILE_NAME = ".settings"

def get_opt_val(opts, key, key_long, default_value):
    for opt in opts:
        if opt[0] in (key, key_long):
            return opt[1]
    return default_value

def read_settings(settings_file):
    with open(settings_file) as file:
        return yaml.load(file, Loader=yaml.FullLoader)

def read_config(config_file):
    with open(config_file) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config

def write_config(config_file, config):
    with open(config_file, 'w') as file:
        conf_values = yaml.dump(config, file, sort_keys=True)
        print(conf_values)

def write_ignore(ignore_file):
    with open(ignore_file,'w+') as file:
        file.writelines([".pixignore\n", ".pixync\n", ".dtrash/\n"])

def get_absolute_path_with_trailing_slash(local_repo_path):
    local_repo_path = os.path.abspath(local_repo_path)

    if not local_repo_path.endswith(os.path.sep):
        local_repo_path = local_repo_path + os.path.sep
    
    return local_repo_path

def get_remote_repos(config):
    if config['repos']:
        return config['repos']
    else:
        return []

def get_repo(repos, remote_repo_name):
    #print("remote_repo_name: ", remote_repo_name)
    for repo in repos:
    #    print(repo)
        for key, value in repo.items():
            if key == 'name' and value == remote_repo_name:
    #            print(value)
                return repo
    return None

def set_repo_url(repos, remote_repo_name, remote_repo_url):
    #print("remote_repo_name: ", remote_repo_name)
    for repo in repos:
    #    print(repo)
        for key, value in repo.items():
            if key == 'name' and value == remote_repo_name:
                repo['url'] = remote_repo_url
                print(repo)
                return
                
    print('remote repo \'{}\' not found'.format(remote_repo_name))
    return

def config_repos_add(config, repo_name, repo_url):
    remote_repos = get_remote_repos(config)

    if get_repo(remote_repos, repo_name):
        print('repo exists already.')
        return
        
    remote_repos.insert(0,{'name':repo_name, 'url': repo_url})
    config['repos'] = remote_repos

def config_repos_set_url(config, repo_name, repo_url):
    remote_repos = get_remote_repos(config)
    for repo in remote_repos:
        for key, value in repo.items():
            if key == 'name' and value == repo_name:
                repo['url'] = repo_url
                return
                
    print('remote repo \'{}\' not found'.format(repo_name))
    return

def config_repos_list(config, long=False):
    remote_repos = get_remote_repos(config)
    for repo in remote_repos:
        if long:
            print(repo['name'], repo['url'])
        else:
            print(repo['name'])

def config_repos_rename(config, repo_old_name, repo_new_name):
    remote_repos = get_remote_repos(config)
    for repo in remote_repos:
        for key, value in repo.items():
            if key == 'name' and value == repo_old_name:
                repo['name'] = repo_new_name
                return
                
    print('remote repo \'{}\' not found'.format(repo_old_name))
    return

def get_path_by_ext(ext_mappings, ext):
    for k, v in ext_mappings.items():
        if k.lower() == ext.lower()[1:]:
            return v
    return 'tmp'

def get_creation_date(path_to_file):
    return time.strftime('%Y%m%d', time.localtime(os.path.getctime(path_to_file)))

def get_default_local_repo_path(remote_repo_url):
    path_comp = os.path.split(remote_repo_url)
    dir_name = path_comp[len(path_comp)-1]
    return os.getcwd() + os.path.sep  + dir_name
    
def cmd_help():
    print(sys.argv[0], "push|pull|help")

def cmd_pull(remote_repo_name, local_repo_path = os.getcwd()):

    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)

    config_file = local_repo_path + CONFIG_FILE_NAME
    config = read_config(config_file)
    repos = get_remote_repos(config)
    
    repo = get_repo(repos, remote_repo_name)

    if repo == None:
        print("remote repository '{}' not found.".format(remote_repo_name))
        exit(1)

    if repo['url'].endswith(os.path.sep):
        remote_url = repo['url']
    else:
        remote_url = repo['url'] + os.path.sep

    if repo != None:
        subprocess.call(['rsync','-urtWv', '--progress', remote_url , local_repo_path])
        print ('pull from \'', remote_repo_name ,'\' complete.')
    else:
        print ('repo \'', remote_repo_name, '\' not found.')


def cmd_push(remote_repo_name, local_repo_path = os.getcwd()):

    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)

    config_file = local_repo_path + CONFIG_FILE_NAME
    config = read_config(config_file)
    repos = get_remote_repos(config)
    repo = get_repo(repos, remote_repo_name)

    if repo['url'].endswith(os.path.sep):
        remote_url = repo['url']
    else:
        remote_url = repo['url'] + os.path.sep

    print('remote_url: ', remote_url)
    print('local_path: ', local_repo_path)
    
    if repo != None:
        subprocess.call(['rsync','-urtWv','--exclude-from=.pixignore', '--progress' , local_repo_path, remote_url])
        print ("push to '{}' complete.".format(remote_url))
    else:
        print ("repo '{}' not found.".format(remote_repo_name))

    
def cmd_clone(remote_repo_url, remote_repo_name, local_repo_path = '__DEFAULT__'):
    if local_repo_path == '__DEFAULT__':
        local_repo_path = get_absolute_path_with_trailing_slash(get_default_local_repo_path(remote_repo_url))
    else:
        local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path) 

    print(local_repo_path)
    os.makedirs(local_repo_path)
    print("local directory '{}' created.".format(local_repo_path))
    repos = [{'name':remote_repo_name,'url':remote_repo_url}]
    config = {'repos': repos}
    write_config(local_repo_path + CONFIG_FILE_NAME, config)
    print("config file created")
    write_ignore(local_repo_path + IGNORE_FILE_NAME)
    print('ignore file created')
    cmd_pull(remote_repo_name, local_repo_path)

def cmd_init(local_repo_path = os.getcwd()):
    print('=== cmd_init ===')
    print('local_repo_path:', local_repo_path)

    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)

    config = {'repos': []}

    Path(local_repo_path).mkdir(parents=True, exist_ok=True)

    write_config(local_repo_path + CONFIG_FILE_NAME, config)
    write_ignore(local_repo_path + IGNORE_FILE_NAME)


    print('local repository {} initialized successfully.'.format(local_repo_path))

def cmd_import(drive_path, local_repo_path, cam_name, delete=False):

    ext_mappings = {}

    for cat_key, cat_value in settings['ext-mappings'].items():
        for subcat_key, subcat_value in cat_value.items():
            for ext in subcat_value:
                ext_mappings[ext] = cat_key + os.path.sep + subcat_key
    
    print(ext_mappings)

    files = glob.iglob(drive_path + '/**/*.*', recursive=True)
    file_count = len(glob.glob(drive_path + '/**/*.*', recursive=True))
    running_count = 1
    for file in files:
        print ('[{}/{}]\t{}'.format(running_count, file_count, file))
        creation_date = get_creation_date(file)
        filename, file_extension = os.path.splitext(file)
        dest = local_repo_path + os.path.sep + get_path_by_ext(ext_mappings, file_extension) + os.path.sep + creation_date + '_'+ cam_name + '_' + os.path.basename(file)
        if delete:
            subprocess.call(['rsync', '-t', '--delete-source-files', file, dest])
        else:
            subprocess.call(['rsync', '-t', file, dest])

        running_count = running_count + 1

def cmd_remote_ls(long, local_repo_path = os.getcwd()):
    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)
    config = read_config(local_repo_path + CONFIG_FILE_NAME)
    config_repos_list(config, long)

def cmd_remote_set_url(remote_repo_name, remote_repo_url, local_repo_path = os.getcwd()):
    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)
    config = read_config(local_repo_path + CONFIG_FILE_NAME)
    config_repos_set_url(config, remote_repo_name, remote_repo_url)
    write_config(local_repo_path + CONFIG_FILE_NAME, config)

def cmd_remote_add(remote_repo_name, remote_repo_url, local_repo_path = os.getcwd()):
    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)
    config = read_config(local_repo_path + CONFIG_FILE_NAME)
    config_repos_add(config, remote_repo_name, remote_repo_url)
    print('config:', config)
    write_config(local_repo_path + CONFIG_FILE_NAME, config)
    subprocess.call(['rsync', '-a', '-f+ */', '-f- *', local_repo_path, remote_repo_url])

def cmd_remote_rename(remote_repo_old_name, remote_repo_new_name, local_repo_path = os.getcwd()):
    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)
    config = read_config(local_repo_path + CONFIG_FILE_NAME)
    config_repos_rename(config, remote_repo_old_name, remote_repo_new_name)
    write_config(local_repo_path + CONFIG_FILE_NAME, config)

def cmd_remote_remove(remote_repo_name, local_repo_path = os.getcwd()):
    print('TODO: not implemented')

settings = read_settings(os.path.expanduser('~') + os.path.sep + SETTINGS_FILE_NAME)

