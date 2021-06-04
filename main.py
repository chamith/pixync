#! /bin/python3

import argparse
import os
import procedures

parser = argparse.ArgumentParser(
    description='Synchronizes the photos amoung multiple repositories', prog="pixync")

parser.add_argument('-p', '--local-repo-path', dest='local_repo_path', help='local repository path')

common_parser = argparse.ArgumentParser()
common_parser.add_argument('-p', '--local-repo-path', dest='local_repo_path', help='local repository path')

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
import_parser.add_argument('-c', '--camera-name', dest='cam_name', help='camera id')
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

if args.local_repo_path:
    local_repo_path = args.local_repo_path
else:
    local_repo_path = os.getcwd()

if args.func == 'init':
    procedures.cmd_init(local_repo_path)

elif args.func == 'clone':
    procedures.cmd_clone(args.remote_repo_url, args.remote_repo_name, local_repo_path)

elif args.func == 'pull':
    procedures.cmd_pull(args.remote_repo_name, local_repo_path)

elif args.func == 'push':
    procedures.cmd_push(args.remote_repo_name, local_repo_path)

elif args.func == 'import':
    procedures.cmd_import(args.media_source_path, local_repo_path, args.cam_name, args.delete_source_files)

elif args.func == 'remote':
    if args.remote_func == 'ls':
        procedures.cmd_remote_ls(args.remote_ls_l, local_repo_path)
    if args.remote_func == 'add':
        procedures.cmd_remote_add(args.remote_repo_name, args.remote_repo_url, local_repo_path)
    elif args.remote_func == 'set-url':
        procedures.cmd_remote_set_url(args.remote_repo_name, args.remote_repo_url, local_repo_path)
    elif args.remote_func == 'rename':
        procedures.cmd_remote_rename(args.remote_repo_old_name, args.remote_repo_new_name, local_repo_path)
    elif args.remote_func == 'remove':
        procedures.cmd_remote_remove(args.remote_repo_name, local_repo_path)