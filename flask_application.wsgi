import site, os
site.addsitedir(os.path.dirname(__file__))

from flask_application import app as application
