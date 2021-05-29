#! /bin/python3

import sys
import getopt
import subprocess
import yaml
import os

def get_opt_val(opts, key, key_long, default_value):
    for opt in opts:
        if opt[0] in (key, key_long):
            return opt[1]
    return default_value

def read_config():
    global config
    with open(config_file) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config

def write_config(config_file):
    with open(config_file, 'w') as file:
        print(config)
        conf_values = yaml.dump(config, file, sort_keys=True)
        print(conf_values)

def get_remote_repos():
    return config['repos']

config_file = os.getcwd() + "/.pixync"
config = read_config()
repos = get_remote_repos()

commandLineArgs = sys.argv[1:]
shortOpt = "duhr:"
longOpt = ["pull", "push","help", "repo="]

def get_repo(repo_name):
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

def cmd_pull(repo_name):
    repo = get_repo(repo_name)

    if repo != None:
        subprocess.call(['rsync','-urtWv', '--progress', repo['url'] , './'])
        print ('pull from \'', repo_name ,'\' complete.')
    else:
        print ('repo \'', repo_name, '\' not found.')


def cmd_push(repo_name):
    repo = get_repo(repo_name)
    if repo != None:
        subprocess.call(['rsync','-urtWv', '--progress' , './', repo['url']])
        print ('push to \'', repo_name ,'\' complete.')
    else:
        print ('repo \'', repo_name, '\' not found.')

def cmd_clone(repo_url, repo_name):
    repos = [{'name',repo_name},{'url',repo_url}]
    config['repos'] = repos
    write_config()

opts, args = getopt.getopt(commandLineArgs, shortOpt, longOpt)

print(opts, args)

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
elif args[0] == 'remote':
    write_config()