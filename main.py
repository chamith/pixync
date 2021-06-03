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
# init_parser.add_argument('-p','--local-repo-path', dest='local_repo_path', help='local repository path')

# clone
clone_parser = func_parser.add_parser('clone', parents=[common_parser], add_help=False)
clone_parser.add_argument('remote_repo_url', metavar='remote-repo-url', help='remote repository url')
clone_parser.add_argument('-r', '--remote-repo-name', dest='remote_repo_name', help='remote repository name', default='origin')
# clone_parser.add_argument('-p', '--local-repo-path', dest='local_repo_path', help='local repository path')

# pull
pull_parser = func_parser.add_parser('pull', parents=[common_parser], add_help=False)
pull_parser.add_argument('remote_repo_name', metavar='remote-repo-name', help='remote repository name')
# pull_parser.add_argument('-p','--local-repo-path', dest='local_repo_path', help='local repository path', default='.')

# push
push_parser = func_parser.add_parser('push', parents=[common_parser], add_help=False)
push_parser.add_argument('remote_repo_name', metavar='remote-repo-name', help='remote repository name')
# push_parser.add_argument('-p','--local-repo-path', dest='local_repo_path', help='local repository path', default='.')

# import
import_parser = func_parser.add_parser('import', parents=[common_parser], add_help=False)
import_parser.add_argument('source', metavar='media-path', help='media path')
import_parser.add_argument('dest', metavar='local-repo-path', help='local repository path')
import_parser.add_argument('--camera-id', dest='cam', help='camera id')

# remote
remote_parser = func_parser.add_parser('remote', parents=[common_parser], add_help=False)
# remote_parser.add_argument('-p','--local-repo-path', dest='local_repo_path', help='local repository path')
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

if args.func == 'init':
    # print('init')
    # print('local-repo-path:', args.local_repo_path)

    if args.local_repo_path:
        procedures.cmd_init(args.local_repo_path)
    else:
        procedures.cmd_init()

elif args.func == 'clone':
    if args.local_repo_path:
        procedures.cmd_clone(args.remote_repo_url, args.remote_repo_name, args.local_repo_path)
    else:
        procedures.cmd_clone(args.remote_repo_url, args.remote_repo_name)

elif args.func == 'pull':
    if args.local_repo_path:
        procedures.cmd_pull(args.remote_repo_name, args.local_repo_path)
    else:
        procedures.cmd_pull(args.remote_repo_name)

elif args.func == 'push':
    if args.local_repo_path:
        procedures.cmd_push(args.remote_repo_name, args.local_repo_path)
    else:
        procedures.cmd_push(args.remote_repo_name)

elif args.func == 'remote':
    if args.remote_func == 'ls':
        # print('remote_ls')
        # print('l:', args.remote_ls_l)
        procedures.cmd_remote_ls(args.remote_ls_l)
    if args.remote_func == 'add':
        # print('remote_add')
        # print('remote-repo-name:', args.remote_repo_name)
        # print('remote-repo-url:', args.remote_repo_url)
        procedures.cmd_remote_add(args.remote_repo_name, args.remote_repo_url)
    elif args.remote_func == 'set-url':
        # print('remote_seturl')
        # print('remote-repo-name:', args.remote_repo_name)
        # print('remote-repo-url:', args.remote_repo_url)
        procedures.cmd_remote_set_url(args.remote_repo_name, args.remote_repo_url)
    elif args.remote_func == 'rename':
        # print('remote_rename')
        # print('remote-repo-old-name:', args.remote_repo_old_name)
        # print('remote-repo-new-name:', args.remote_repo_new_name)
        procedures.cmd_remote_rename(args.remote_repo_old_name, args.remote_repo_new_name)
    elif args.remote_func == 'remove':
        # print('remote_remove')
        # print('remote-repo-name:', args.remote_repo_name)
        procedures.cmd_remote_remove(args.remote_repo_name)