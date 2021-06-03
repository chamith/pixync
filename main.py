#! /bin/python3

import argparse
import os
import procedures

def cmd_init(repo_url, repo_name, local_dir_path = os.getcwd()):
    print('cmd_init')

def cmd_clone(repo_url, repo_name):
    print('cmd_clone')

def get_input(title, arg):
    if arg:
        return arg
    else:
        print(title, ': ', end='')
        return input()

parser = argparse.ArgumentParser(
    description='Synchronizes the photos amoung multiple repositories', prog="pixync")
# parser.add_argument('action', choices=['init','import'])
# args = parser.parse_args(['init'])

func_parser = parser.add_subparsers(title="command", dest='func')

# init
init_parser = func_parser.add_parser('init')
init_parser.add_argument('url',metavar='remote-repo-url', help='remote repository url')
init_parser.add_argument('-a', '--remote-repo-name', required=True, dest='name', help='remote repository name')
init_parser.add_argument('-p', '--local-repo-path', dest='path', help='local repository path')

# clone
clone_parser = func_parser.add_parser('clone')
clone_parser.add_argument('url',metavar='remote-repo-url', help='remote repository url')
clone_parser.add_argument('--remote-repo-name', dest='name', help='remote repository name')

# pull
pull_parser = func_parser.add_parser('pull')
pull_parser.add_argument('name', metavar='remote-repo-name', help='remote repository name')
pull_parser.add_argument('--local-repo-path', dest='path', help='local repository path', default='.')

# push
push_parser = func_parser.add_parser('push')
push_parser.add_argument('name', metavar='remote-repo-name', help='remote repository name')
push_parser.add_argument('--local-repo-path', dest='path', help='local repository path', default='.')

# import
import_parser = func_parser.add_parser('import')
import_parser.add_argument('source', metavar='media-path', help='media path')
import_parser.add_argument('dest', metavar='local-repo-path', help='local repository path')
import_parser.add_argument('--camera-id', dest='cam', help='camera id')

# remote
remote_parser = func_parser.add_parser('remote')
remote_func_parser = remote_parser.add_subparsers(title='remote function', dest='remote_func')

# remote add
remote_add_parser = remote_func_parser.add_parser('add')
remote_add_parser.add_argument('remote_repo_name', metavar='name')
remote_add_parser.add_argument('remote_repo_url', metavar='url')

# remote set-url
remote_add_parser = remote_func_parser.add_parser('set-url')
remote_add_parser.add_argument('remote_repo_name', metavar='name')
remote_add_parser.add_argument('remote_repo_url', metavar='url')

# remote rename
remote_add_parser = remote_func_parser.add_parser('rename')
remote_add_parser.add_argument('remote_repo_old_name', metavar='old_name')
remote_add_parser.add_argument('remote_repo_new_name', metavar='new_name')

# remote remove
remote_add_parser = remote_func_parser.add_parser('remove')
remote_add_parser.add_argument('remote_repo_name', metavar='name')

args = parser.parse_args()

if args.func == 'init':
    print('init')
    
    name = get_input('remote repository name', args.name)
    
    print('remote-repo-url:', args.url)
    print('remote-repo-name:', name)
    print('local-repo-path:', args.path)

    if args.path:
        procedures.cmd_init(args.url, name, args.path)
    else:
        procedures.cmd_init(args.url, name)

elif args.func == 'clone':
    print('clone')

elif args.func == 'remote':
    if args.remote_func == 'add':
        print('remote_add')
        print('remote-repo-name:', args.remote_repo_name)
        print('remote-repo-url:', args.remote_repo_url)
        procedures.cmd_remote_add(args.remote_repo_name, args.remote_repo_url)
    elif args.remote_func == 'set-url':
        print('remote_seturl')
        print('remote-repo-name:', args.remote_repo_name)
        print('remote-repo-url:', args.remote_repo_url)
        procedures.cmd_remote_set_url(args.remote_repo_name, args.remote_repo_url)
    elif args.remote_func == 'rename':
        print('remote_rename')
        print('remote-repo-old-name:', args.remote_repo_old_name)
        print('remote-repo-new-name:', args.remote_repo_new_name)
        procedures.cmd_remote_rename(args.remote_repo_old_name, args.remote_repo_new_name)
    elif args.remote_func == 'remove':
        print('remote_remove')
        print('remote-repo-name:', args.remote_repo_name)
        procedures.cmd_remote_remove(args.remote_repo_name)