#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Run 'fab --list' to see list of available commands.

References:
# http://docs.fabfile.org/
'''

from __future__ import with_statement, print_function
import os
import sh
import sys
import random
import string

from colorama import Fore, Back, Style
from invoke import task, env

from fabric import Connection, SerialGroup

APP_NAME = "app"
PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_NAME = "example.com"

hosts = ['user@remotehost']
code_dir = '/path/to/repos/destination'
sys.path.append(PROJ_DIR)

"""
def _transfer_files(src, dst, ssh_port=None):
    ssh_port = ssh_port or 22
    assert os.getenv('SSH_AUTH_SOCK') is not None # Ensure ssh-agent is running
    if not src.endswith('/'):
        src = src + '/'
    if dst.endswith('/'):
        dst = dst[:-1]
    local('rsync -avh --delete-before --copy-unsafe-links -e'
          '"ssh -p {0}" {1} {2}'.format(ssh_port, src, dst))
"""


@task
def pre_deploy(c):
    '''Add, commit and push the Git repo before final deployment.'''
    local("git add -p && git commit && git push")


@task
def deploy(c):
    '''Final deployment of the application'''
    with c.cd(code_dir):
        for cxn in SerialGroup(hosts):
            cxn.run("git pull")
            cxn.run(f"touch {APP_NAME}.wsgi")
            # run("sudo apachectl restart")


@task
def init(c, site_name=SITE_NAME):
    '''Call env_setup, env_init, and skeletonize for one-step init'''
    print(Fore.GREEN + "Call env_setup, env_init, and"
          "skeletonize for one-step init:")
    env_setup(c)
    env_init(c, site_name=site_name)
    skeletonize(c)


@task
def env_init(c, site_name=SITE_NAME):
    '''Initialize with this site hostname.'''
    print(Fore.GREEN + "Initializing new site configuration...")

    #
    # Generate secret key and update config file
    #
    CHARS = string.ascii_letters + string.digits
    SECRET_KEY = "".join([random.choice(CHARS) for i in range(50)])

    print(Fore.BLUE + "Configuring the secret key...")
    with c.cd(PROJ_DIR):
        try:
            sh.sed("-i ",
                   "s/SECRET_KEY *=.*/SECRET_KEY = '{0}'/g".format(SECRET_KEY),
                   "{0}/config.py".format(APP_NAME))
        except sh.ErrorReturnCode:
            print(Fore.RED + "Could not configure SECRET_KEY for config.py")
            exit(1)

    #
    # Set the site name, the user defined site hostname
    #
    print(Fore.BLUE + "Configuring the SITE_NAME '{0}'.".format(site_name))
    try:
        sh.sed("-i ",
               "s/SITE_NAME *=.*/SITE_NAME = '{0}'/g".format(site_name),
               "{0}/config.py".format(APP_NAME))
    except sh.ErrorReturnCode:
        print(Fore.RED + "Could not configure SITE_NAME for config.py")
        exit(1)


@task
def env_setup(c):
    '''Initialize environment with requisite Python modules.'''
    print(Fore.GREEN + "Installing requisite modules...")

    # Install our requistite modules for the website.
    sh.pip("install", r="requirements.txt")


@task
def skeletonize(c):
    '''Update Skeleton HTML5-Boilerplate.'''
    print(Fore.GREEN + "Skeletonizing the project directory...")

    # Skeleton
    print(Fore.BLUE + "Installing skeleton HTML5 Boilerplate.")
    os.chdir(PROJ_DIR)
    sh.git.submodule.update(init=True)

    os.chdir(PROJ_DIR + "/Skeleton")
    sh.git.pull("origin", "master")
    sh.rsync("-av", "images", "{0}/{1}/static/".format(PROJ_DIR, APP_NAME))
    sh.rsync("-av", "css", "{0}/{1}/static/".format(PROJ_DIR, APP_NAME))
    sh.rsync("-av", "index.html",
             "{0}/{1}/templates/base_t.html".format(PROJ_DIR, APP_NAME))
    os.chdir(PROJ_DIR)

    # Patch the base template with templating tags
    print(Fore.BLUE + "Patching the base template.")
    os.chdir(PROJ_DIR + "/{0}/templates/".format(APP_NAME))
    template_patch = open("base_t.patch".format(APP_NAME))
    sh.patch(strip=0, _in=template_patch)
    template_patch.close()
    os.chdir(PROJ_DIR)

    # jQuery
    print(Fore.BLUE + "Installing jquery 1.9.0.")
    os.chdir(PROJ_DIR + "/" + APP_NAME + "/static/js")
    sh.curl("http://code.jquery.com/jquery-1.9.0.min.js")
    os.chdir(PROJ_DIR)


@task
def console(c):
    '''Load the application in an interactive console.'''
    c.run('env DEV=yes python -i runserver.py')


@task
def server(c):
    '''Run the dev server'''
    
    with c.cd(PROJ_DIR):
        env = os.environ.copy()
        env['DEV'] = 'yes'
        c.run('./runserver.py', env=env)


@task
def test(c):
    '''Run the test suite'''
    c.run('env TEST=yes python tests.py')


@task
def clean(c):
    '''Clear the cached .pyc files.'''
    c.run("find . \( -iname '*.pyc' -o -name '*~' \) -exec rm -v {} \;")
"""
@task
def server_setup(c):
    '''Setup the server environment.'''
    global SITE_NAME

    local_dir = os.getcwd()
    remote_dir = os.path.join('/home', os.getlogin(), 'web', SITE_NAME,
                              'private', SITE_NAME)
    run('mkdir -p {0}'.format(remote_dir))
    _transfer_files(local_dir, env.host + ':' + remote_dir, ssh_port=env.port)
    run('cd {0} && bash setup/server_setup.bash {1}'.format(remote_dir,
                                                            SITE_NAME))
"""
