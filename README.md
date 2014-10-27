Flask-Boilerplate
======================

This is a bootstrap site for [Flask](http://flask.pocoo.org/) that utilizes [Fabric](http://fabfile.org) and [Skeleton](http://www.getskeleton.com/) to get you up-and-running with a responsive Flask web app.

Getting Started
-----------------

It is suggested that you use
[virtualenvwrapper](http://pypi.python.org/pypi/virtualenvwrapper) when
developing this website. This will allow you to isolate your organization's 
development environment from the rest of your system, ensuring that you
are developing with the proper software.

To do development work on a new website, run the following commands from
the root directory of your cloned site to get started:

-   `fab init:site_name=<sitename>`
    - Where "`<sitename>`" is replaced with the hostname of your new site      
-   `fab skeletonize`
    - Installs Skeleton and JQuery, patching the base templates along the way.
-   `fab server`
    - Will run a local dev server on `http://localhost:8080`

You will then be able to access the website at http://localhost:8080.
Changes in the code will automatically reload the web server when necessary.

In production, the server uses WSGI, so please don't rename or move
`__init__.py` in the root of the repository.
