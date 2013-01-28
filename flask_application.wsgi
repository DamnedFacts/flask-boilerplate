import site, os
site.addsitedir(os.path.dirname(__file__))

from saintnicholas import app as application
