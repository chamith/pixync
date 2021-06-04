#! /bin/python3

import argparse
import subprocess
import yaml
import os
import glob
import time
import shutil

CONFIG_FILE_NAME = ".pixync"
IGNORE_FILE_NAME = ".pixignore"
SETTINGS_FILE_NAME = ".settings"

def read_settings(settings_file):
    with open(settings_file) as file:
        return yaml.load(file, Loader=yaml.FullLoader)

def read_config(config_file):
    with open(config_file) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config

def write_config(config_file, config):
    if verbose: print("Writing the config file '{}'".format(config_file))
    with open(config_file, 'w') as file:
        yaml.dump(config, file, sort_keys=True)

def write_ignore(ignore_file):
    if verbose: print("Writing the ignore file '{}'".format(ignore_file))
    with open(ignore_file,'w+') as file:
        file.writelines([".pixignore\n", ".pixync\n", ".dtrash/\n"])

def get_path_with_trailing_slash(remote_path):
    if not remote_path.endswith(os.path.sep):
        return remote_path + os.path.sep
    return remote_path

def get_absolute_path_with_trailing_slash(local_repo_path):
    return get_path_with_trailing_slash(os.path.abspath(local_repo_path))

def get_remote_repos(config):
    if config['repos']: return config['repos']
    return []

def get_repo(repos, remote_repo_name):
    for repo in repos:
        for key, value in repo.items():
            if key == 'name' and value == remote_repo_name:
                return repo
    return None

def set_repo_url(repos, remote_repo_name, remote_repo_url):
    for repo in repos:
        for key, value in repo.items():
            if key == 'name' and value == remote_repo_name:
                repo['url'] = remote_repo_url
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
        if long: print(repo['name'], repo['url'])
        else: print(repo['name'])

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
        if k.lower() == ext.lower()[1:]: return v
    return 'tmp'

def get_creation_date(path_to_file):
    return time.strftime('%Y%m%d', time.localtime(os.path.getctime(path_to_file)))

def get_default_local_repo_path(remote_repo_url):
    path_comp = os.path.split(remote_repo_url)
    dir_name = path_comp[len(path_comp)-1]
    return os.getcwd() + os.path.sep  + dir_name

def cmd_pull(remote_repo_name, local_repo_path = os.getcwd()):
    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)

    config_file = local_repo_path + CONFIG_FILE_NAME
    config = read_config(config_file)
    repos = get_remote_repos(config)
    repo = get_repo(repos, remote_repo_name)

    if repo == None:
        print("remote repository '{}' not found.".format(remote_repo_name))
        exit(1)

    remote_repo_url = get_path_with_trailing_slash(repo['url'])

    if verbose:
        print("--- pull ---")
        print('remote_repo_url:\t ', remote_repo_url)
        print('local_repo_path:\t ', local_repo_path)
    
    rsync_command = ['rsync','-urtW', remote_repo_url, local_repo_path]

    if verbose:
        rsync_command.insert(2,'-v')
        rsync_command.insert(2,'--progress')
    
    subprocess.call(rsync_command)

    print ("Pull from '{}' to '{}' completed.".format(remote_repo_url, local_repo_path))

def cmd_push(remote_repo_name, local_repo_path = os.getcwd()):
    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)
    config_file = local_repo_path + CONFIG_FILE_NAME
    config = read_config(config_file)
    repos = get_remote_repos(config)
    repo = get_repo(repos, remote_repo_name)

    if repo == None:
        print("remote repository '{}' not found.".format(remote_repo_name))
        exit(1)

    remote_repo_url = get_path_with_trailing_slash(repo['url'])

    if verbose:
        print("---push---")
        print('remote_repo_url: ', remote_repo_url)
        print('local_repo_path: ', local_repo_path)
    
    rsync_command = ['rsync','-urtW','--exclude-from=.pixignore', local_repo_path, remote_repo_url]

    if verbose:
        rsync_command.insert(2,'-v')
        rsync_command.insert(2,'--progress')
    
    subprocess.call(rsync_command)

    print ("Push from '{}' to '{}' complete.".format(local_repo_path, remote_repo_url))
    
def cmd_clone(remote_repo_url, remote_repo_name, local_repo_path = os.getcwd()):
    if local_repo_path == os.getcwd():
        local_repo_path = get_absolute_path_with_trailing_slash(get_default_local_repo_path(remote_repo_url))
    else:
        local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path) 

    if verbose:
        print("---clone---")
        print('remote_repo_url: ', remote_repo_url)
        print('local_repo_path: ', local_repo_path) 

    if os.path.exists(local_repo_path + CONFIG_FILE_NAME):
        print("Repository '{}' already exists.".format(local_repo_path))
        exit(1)

    os.makedirs(local_repo_path)
    config = {'repos': [{'name':remote_repo_name,'url':remote_repo_url}]}
    write_config(local_repo_path + CONFIG_FILE_NAME, config)
    write_ignore(local_repo_path + IGNORE_FILE_NAME)
    cmd_pull(remote_repo_name, local_repo_path)
    print('Remote repository \'{}\' cloned into \'{}\' successfully.'.format(remote_repo_url))

def cmd_init(local_repo_path = os.getcwd()):
    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)

    if verbose:
        print("---init---")
        print('local_repo_path: ', local_repo_path) 

    config = {'repos': []}
    os.makedirs(local_repo_path, exist_ok=True)

    write_config(local_repo_path + CONFIG_FILE_NAME, config)
    write_ignore(local_repo_path + IGNORE_FILE_NAME)

    print('Local repository {} initialized successfully.'.format(local_repo_path))

def cmd_import(media_source_path, local_repo_path, cam_name, delete_source_files=False):
    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)
    ext_mappings = {}
    for cat_key, cat_value in settings['ext-mappings'].items():
        for subcat_key, subcat_value in cat_value.items():
            for ext in subcat_value:
                ext_mappings[ext] = cat_key + os.path.sep + subcat_key

    local_temp_dir = local_repo_path + os.path.sep + '__CACHE__'

    if verbose:
        print("---import---")
        print("media_source_path:\t", media_source_path)
        print("local_repo_path:\t", local_repo_path)

    rsync_command = ['rsync', '-urtW', media_source_path, local_temp_dir]

    if verbose:
        rsync_command.insert(2,'-v')
        rsync_command.insert(2,'--progress')

    if delete_source_files:
        rsync_command.insert(2,'--remove-source-files')

    if verbose: print('Caching the files in the local repo path.')
    subprocess.call(rsync_command)
    if verbose: print('Caching the files in the local repo path completed.')

    if verbose: print('Moving & Renaming files in the local repo.')
    for file in glob.iglob(local_temp_dir + '/**/*.*', recursive=True):
        creation_date = get_creation_date(file)
        filename, file_extension = os.path.splitext(file)
        dest_sub_dir = local_repo_path + get_path_by_ext(ext_mappings, file_extension)
        dest = dest_sub_dir+ os.path.sep + creation_date + '_'+ cam_name + '_' + os.path.basename(file)
        os.makedirs(dest_sub_dir, exist_ok=True)
        os.rename(file, dest)

    if verbose: print('Moving & Renaming files in the local repo completed.')

    if verbose: print('Removing temporary files & directories.')
    shutil.rmtree(local_temp_dir)

    print("File import completed successfully.")

def cmd_remote_ls(long, local_repo_path = os.getcwd()):
    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)
    config = read_config(local_repo_path + CONFIG_FILE_NAME)
    config_repos_list(config, long)

def cmd_remote_set_url(remote_repo_name, remote_repo_url, local_repo_path = os.getcwd()):
    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)
    config = read_config(local_repo_path + CONFIG_FILE_NAME)
    config_repos_set_url(config, remote_repo_name, remote_repo_url)
    write_config(local_repo_path + CONFIG_FILE_NAME, config)
    print("URL of the remote repository '{}' is set to '{}' successfully.".format(remote_repo_name, remote_repo_url))

def cmd_remote_add(remote_repo_name, remote_repo_url, local_repo_path = os.getcwd()):
    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)
    config = read_config(local_repo_path + CONFIG_FILE_NAME)
    config_repos_add(config, remote_repo_name, remote_repo_url)
    write_config(local_repo_path + CONFIG_FILE_NAME, config)
    subprocess.call(['rsync', '-a', '-f+ */', '-f- *', local_repo_path, remote_repo_url])
    print("Remote repository '{}' [{}] added successfully.".format(remote_repo_name, remote_repo_url))

def cmd_remote_rename(remote_repo_old_name, remote_repo_new_name, local_repo_path = os.getcwd()):
    local_repo_path = get_absolute_path_with_trailing_slash(local_repo_path)
    config = read_config(local_repo_path + CONFIG_FILE_NAME)
    config_repos_rename(config, remote_repo_old_name, remote_repo_new_name)
    write_config(local_repo_path + CONFIG_FILE_NAME, config)
    print("Remote repository '{}' renamed to '{}' successfully.".format(remote_repo_old_name, remote_repo_new_name))

def cmd_remote_remove(remote_repo_name, local_repo_path = os.getcwd()):
    print('TODO: not implemented')

settings = read_settings(os.path.expanduser('~') + os.path.sep + SETTINGS_FILE_NAME)

common_parser = argparse.ArgumentParser()
common_parser.add_argument('-p', '--local-repo-path', dest='local_repo_path', help='local repository path')
info_group = common_parser.add_mutually_exclusive_group()
info_group.add_argument('-v', '--verbose', action='store_true')
info_group.add_argument('-q', '--quiet', action='store_false')

parser = argparse.ArgumentParser(
    description='Synchronizes the photos amoung multiple repositories', prog="pixync" , add_help=False, parents=[common_parser])

# function
func_parser = parser.add_subparsers(title="command", dest='func')

# init
init_parser = func_parser.add_parser('init', parents=[common_parser], add_help=False)

# clone
clone_parser = func_parser.add_parser('clone', parents=[common_parser], add_help=False)
clone_parser.add_argument('remote_repo_url', metavar='remote-repo-url', help='remote repository url')
clone_parser.add_argument('-r', '--remote-repo-name', dest='remote_repo_name', help='remote repository name', default='origin')

# pull
pull_parser = func_parser.add_parser('pull', parents=[common_parser], add_help=False)
pull_parser.add_argument('remote_repo_name', metavar='remote-repo-name', help='remote repository name')

# push
push_parser = func_parser.add_parser('push', parents=[common_parser], add_help=False)
push_parser.add_argument('remote_repo_name', metavar='remote-repo-name', help='remote repository name')

# import
import_parser = func_parser.add_parser('import', parents=[common_parser], add_help=False)
import_parser.add_argument('media_source_path', metavar='media-source-path', help='media path')
import_parser.add_argument('-c', '--camera-name', dest='cam_name', help='camera id', required=True)
import_parser.add_argument('--delete-source-files', dest='delete_source_files', action='store_true')

# remote
remote_parser = func_parser.add_parser('remote', parents=[common_parser], add_help=False)
remote_func_parser = remote_parser.add_subparsers(title='remote function', dest='remote_func')

# remote list
remote_list_parser = remote_func_parser.add_parser('ls', parents=[common_parser], add_help=False)
remote_list_parser.add_argument('-l', dest='remote_ls_l', action='store_true')

# remote add
remote_add_parser = remote_func_parser.add_parser('add', parents=[common_parser], add_help=False)
remote_add_parser.add_argument('remote_repo_name', metavar='name')
remote_add_parser.add_argument('remote_repo_url', metavar='url')

# remote set-url
remote_add_parser = remote_func_parser.add_parser('set-url', parents=[common_parser], add_help=False)
remote_add_parser.add_argument('remote_repo_name', metavar='name')
remote_add_parser.add_argument('remote_repo_url', metavar='url')

# remote rename
remote_add_parser = remote_func_parser.add_parser('rename', parents=[common_parser], add_help=False)
remote_add_parser.add_argument('remote_repo_old_name', metavar='old_name')
remote_add_parser.add_argument('remote_repo_new_name', metavar='new_name')

# remote remove
remote_add_parser = remote_func_parser.add_parser('remove', parents=[common_parser], add_help=False)
remote_add_parser.add_argument('remote_repo_name', metavar='name')

args = parser.parse_args()

verbose = args.verbose
quiet = args.quiet

if verbose: print("pixync: destributed image repository management application.")

if args.local_repo_path:
    local_repo_path = args.local_repo_path
else:
    local_repo_path = os.getcwd()

if args.func == 'init': cmd_init(local_repo_path)
elif args.func == 'clone': cmd_clone(args.remote_repo_url, args.remote_repo_name, local_repo_path)
elif args.func == 'pull': cmd_pull(args.remote_repo_name, local_repo_path)
elif args.func == 'push': cmd_push(args.remote_repo_name, local_repo_path)
elif args.func == 'import': cmd_import(args.media_source_path, local_repo_path, args.cam_name, args.delete_source_files)

elif args.func == 'remote':
    if args.remote_func == 'ls': cmd_remote_ls(args.remote_ls_l, local_repo_path)
    elif args.remote_func == 'add': cmd_remote_add(args.remote_repo_name, args.remote_repo_url, local_repo_path)
    elif args.remote_func == 'set-url': cmd_remote_set_url(args.remote_repo_name, args.remote_repo_url, local_repo_path)
    elif args.remote_func == 'rename': cmd_remote_rename(args.remote_repo_old_name, args.remote_repo_new_name, local_repo_path)
    elif args.remote_func == 'remove': cmd_remote_remove(args.remote_repo_name, local_repo_path)