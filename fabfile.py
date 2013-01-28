#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''\
Run 'fab --list' to see list of available commands.

References:
# http://docs.fabfile.org/en/1.0.1/usage/execution.html#how-host-lists-are-constructed
'''

import platform
assert ('2','6') <= platform.python_version_tuple() < ('3','0')

import os
import datetime
import urllib2
import sh

from fabric.api import env, local, sudo, run
from fabric.utils import puts, warn

from fabulous.color import red, green, blue

APP_NAME = "flask_application"
PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_NAME = "example.com"

def _transfer_files(src, dst, ssh_port=None):
    ssh_port = ssh_port or 22
    assert os.getenv('SSH_AUTH_SOCK') is not None # Ensure ssh-agent is running
    if not src.endswith('/'):
        src = src + '/'
    if dst.endswith('/'):
        dst = dst[:-1]
    local('rsync -avh --delete-before --copy-unsafe-links -e "ssh -p {0}" {1} {2}'.format(ssh_port, src, dst), capture=False)


def init(domain_name=SITE_NAME):
    '''Initialize with this domain name.'''
    print green(u"Initializing...")


    #
    # Generate secret key and update config file
    #
    import random
    import string

    CHARS = string.letters + string.digits
    SECRET_KEY = "".join([random.choice(CHARS) for i in range(50)])

    print blue("Configuring the secret key.")
    os.chdir(PROJ_DIR)
    try:
        sh.sed("-i.bak",
               "-es/SECRET_KEY\s*=\s*.*/SECRET_KEY = '{0}'/g".format(SECRET_KEY),
               "{0}/config.py".format(APP_NAME))
        sh.rm(f="config.py.bak")
    except sh.ErrorReturnCode:
        print red("Could not configure SECRET_KEY for config.py")
        exit(1)


    #
    # Set the site name, the user defined domain name
    #
    print blue("Configuring the SITE_NAME '{0}'.".format(domain_name))
    try:
        sh.sed("-i.bak",
               "-es/SITE_NAME\s*=\s*.*/SITE_NAME = '{0}'/g".format(domain_name),
               "{0}/config.py".format(APP_NAME))
        sh.rm(f="config.py.bak")
    except sh.ErrorReturnCode:
        print red("Could not configure SITE_NAME for config.py")
        exit(1)




def env_setup():
    '''Initialize environment.'''
    print green("Installing requisite modules")

    # Install our requistite modules for the website.
    from setup import requires
    with req in requires:
        sh.pip("install", req)

    import platform
    if platform.python_version_tuple() < (2,7):
        sh.pip("install", "unittest2")



def skeletonize():
    '''Update Skeleton HTML5-Boilerplate.'''
    print green("Skeletonizing the project directory...")

    # Skeleton
    print blue("Installing skeleton HTML5 Boilerplate.")
    os.chdir(PROJ_DIR)
    sh.git.submodule.update(init=True)

    os.chdir(PROJ_DIR + "/skeleton")
    sh.git.pull("origin", "master")
    sh.rsync("-av", "images", "{0}/{1}/static/".format(PROJ_DIR,APP_NAME))
    sh.rsync("-av", "stylesheets",  "{0}/{1}/static/".format(PROJ_DIR,APP_NAME))
    sh.rsync("-av", "index.html",  "{0}/{1}/templates/base_t.html".format(PROJ_DIR,APP_NAME))
    os.chdir(PROJ_DIR)

    # Patch the base template with templating tags
    print blue("Patching the base template.")
    os.chdir(PROJ_DIR + "/{0}/templates/".format(APP_NAME))
    template_patch = open("base_t.patch".format(APP_NAME))
    sh.patch(strip=0, _in=template_patch)
    template_patch.close()
    os.chdir(PROJ_DIR)

    # Jquery
    print blue("Installing jquery 1.9.0.")
    os.chdir(PROJ_DIR + "/" + APP_NAME + "/static/js")
    sh.curl("http://code.jquery.com/jquery-1.9.0.min.js", O=True)
    os.chdir(PROJ_DIR)



def console():
    local('env DEV=yes python -i play.py', capture=False)


def server():
    '''Run the dev server'''
    os.chdir(PROJ_DIR)
    sh.python("runserver.py")
    #local('env DEV=yes python runserver.py', capture=False)

def test():
    '''Run the test suite'''
    local('env TEST=yes python tests.py', capture=False)

def clean():
    '''Clear the cached .pyc files.'''
    local("find . -iname '*.pyc' -exec rm -v {} \;", capture=False)




def server_setup():
    '''Setup the server environment.'''
    global SITE_NAME

    local_dir = os.getcwd()
    remote_dir = os.path.join('/home', os.getlogin(), 'web', SITE_NAME, 'private', SITE_NAME)
    run('mkdir -p {0}'.format(remote_dir))
    _transfer_files(local_dir, env.host + ':' + remote_dir, ssh_port=env.port)
    run('cd {0} && bash setup/server_setup.bash {1}'.format(remote_dir, SITE_NAME))


def deploy():
    '''Sync code from here to the servers'''
    global env
    global SITE_NAME

    # Two separate calculations because Mac has HOME=/Users/swaroop and
    # Linux has HOME=/home/swaroop and therefore cannot use the same dirname.
    local_dir = os.path.join(os.getenv('HOME'), 'web', SITE_NAME, 'private', SITE_NAME)
    remote_dir = os.path.join('/home', os.getlogin(), 'web', SITE_NAME, 'private', SITE_NAME)
    _transfer_files(local_dir, env.host + ':' + remote_dir, ssh_port=env.port)
    sudo('apache2ctl graceful')
    try:
        urllib2.urlopen('http://' + env.host_string)
    except urllib2.HTTPError as x:
        warn(colors.red("Failed! Code deployment was a disaster. Apache is throwing {0}.".format(x)))
        showlogs()
        return
    puts(colors.magenta('Success! The {0} server has been updated.'.format(env.host_string)))


def showlogs():
    '''Show logs of the Apache/mod_wsgi server.'''

    def tail_file_if_exists(path):
        sudo('if [[ -f {0} ]]; then tail -20 {0}; fi'.format(path))

    log_dir = os.path.join('/home', os.getlogin(), 'web', SITE_NAME, 'log')
    today = datetime.datetime.today().strftime("%Y%m%d")
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")

    puts(colors.magenta("flask log - today"))
    tail_file_if_exists('{0}/error.{1}.log'.format(log_dir, today))
    puts(colors.magenta("flask log - yesterday"))
    tail_file_if_exists('{0}/error.{1}.log'.format(log_dir, yesterday))

    puts(colors.magenta("apache log"))
    tail_file_if_exists('/var/log/apache2/error.log')



