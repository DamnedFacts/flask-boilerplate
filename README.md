<ORG_NAME> Website
======================

<ORG_NAME>'s website, to be collaboratively edited by members of
<ORG_NAME>'s organizational team.

The website is written in [Flask](http://flask.pocoo.org/).

Development Usage
-----------------

It is suggested that you use
[virtualenvwrapper](http://pypi.python.org/pypi/virtualenvwrapper) when
developing this website. This will allow you to isolate your organization's 
development environment from the rest of your system, ensuring that you
are developing with the proper software.

To do development work on the website, run the following commands from
the root directory:

-   `python setup.py install`
-   `python setup.py develop`
-   `python flask_application/__init__.py`

You will then be able to access the website at http://localhost:8080.
Changes in the code will automatically reload the webserver when necessary.

In production, the server uses WSGI, so please don't rename or move
`__init__.py` in the root of the repository.
