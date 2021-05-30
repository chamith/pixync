#! /bin/python3

from posixpath import sep
import sys
import getopt
import subprocess
import yaml
import os

CONFIG_FILE_NAME = ".pixync"
IGNORE_FILE_NAME = ".pixignore"

def get_opt_val(opts, key, key_long, default_value):
    for opt in opts:
        if opt[0] in (key, key_long):
            return opt[1]
    return default_value

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

def get_remote_repos(config):
    return config['repos']

def get_repo(repos, repo_name):
    #print("repo_name: ", repo_name)
    for repo in repos:
    #    print(repo)
        for key, value in repo.items():
            if key == 'name' and value == repo_name:
    #            print(value)
                return repo
    return None

def cmd_help():
    print(sys.argv[0], "push|pull|help")

def cmd_pull(repo_name, path = os.getcwd()):

    if not path.endswith(os.path.sep):
        path = path + os.path.sep

    config_file = path + CONFIG_FILE_NAME
    config = read_config(config_file)
    repos = get_remote_repos(config)
    
    repo = get_repo(repos, repo_name)

    if repo == None:
        print("remote repository '{}' not found.".format(repo_name))
        exit(1)

    if repo['url'].endswith(os.path.sep):
        remote_url = repo['url']
    else:
        remote_url = repo['url'] + os.path.sep

    if repo != None:
        subprocess.call(['rsync','-urtWv', '--progress', remote_url , path])
        print ('pull from \'', repo_name ,'\' complete.')
    else:
        print ('repo \'', repo_name, '\' not found.')


def cmd_push(repo_name, path = os.getcwd()):

    if not path.endswith(os.path.sep):
        path = path + os.path.sep

    config_file = path + CONFIG_FILE_NAME
    config = read_config(config_file)
    repos = get_remote_repos(config)
    repo = get_repo(repos, repo_name)

    if repo['url'].endswith(os.path.sep):
        remote_url = repo['url']
    else:
        remote_url = repo['url'] + os.path.sep

    print('remote_url: ', remote_url)
    print('local_path: ', path)
    
    if repo != None:
        subprocess.call(['rsync','-urtWv','--exclude-from=.pixignore', '--progress' , path, remote_url])
        print ("push to '{}' complete.".format(remote_url))
    else:
        print ("repo '{}' not found.".format(repo_name))

def cmd_clone(repo_url, repo_name):
    repos = [{'name':repo_name,'url':repo_url}]
    config = {'repos': repos}
    path_comp = os.path.split(repo_url)
    dir_name = path_comp[len(path_comp)-1]
    print("repo_url:", repo_url)
    print("dir_name:", dir_name)
    local_dir_path = os.getcwd() + os.path.sep + dir_name
    print(local_dir_path)
    os.makedirs(local_dir_path)
    print("local directory '{}' created.".format(local_dir_path))
    config_file = local_dir_path + os.path.sep + CONFIG_FILE_NAME
    write_config(config_file, config)
    print("config file created")

    cmd_pull(repo_name, local_dir_path)

def cmd_init(repo_url, repo_name, local_dir_path = os.getcwd()):
    if not local_dir_path.endswith(os.path.sep):
        local_dir_path = local_dir_path + os.path.sep
    
    repos = [{'name':repo_name,'url':repo_url}]
    config = {'repos': repos}

    config_file = local_dir_path + os.path.sep + CONFIG_FILE_NAME
    write_config(config_file, config)
    write_ignore(local_dir_path + os.path.sep + IGNORE_FILE_NAME)
    
    subprocess.call(['rsync', '-a', '-f+ */', '-f- *', local_dir_path, repo_url])

commandLineArgs = sys.argv[1:]
shortOpt = "iduhr:p:"
longOpt = ["pull", "push","help","init", "repo=", "path="]

opts, args = getopt.getopt(commandLineArgs, shortOpt, longOpt)

print('opts: ', opts)
print('args: ', args)

if len(args) == 0:
    cmd_help()
    exit(0)

elif args[0] == 'pull':
    if len(args) > 1:
        cmd_pull(args[1])
    else:
        print("repo not provided")
        cmd_help()

elif args[0] == 'push':
    if len(args) > 1:
        cmd_push(args[1])
    else:
        print("repo not provided")
        cmd_help()

elif args[0] == "clone":
    if len(args) > 2:
        repo_name = args[2]
    else:
        repo_name = "origin"
    
    print(repo_name)
    if len(args) > 1:
        cmd_clone(args[1], repo_name)

elif args[0] == "init":

    opts, inner_args = getopt.getopt(sys.argv[3:], shortOpt, longOpt)
    print('opts: ', opts)
    print('args: ', inner_args)

    if len(args) > 2:
        repo_name = args[2]
    else:
        repo_name = "origin"
        
    if len(args) < 2:
        print("remote url not provided")
        exit(0)
    
    remote_url = args[1]
    cmd_init(remote_url, repo_name)

elif args[0] == 'remote':
    write_config()