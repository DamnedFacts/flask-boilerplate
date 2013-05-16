import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

requires = [
    'flask',
    'wtforms',
    'sqlalchemy',
    'nose',
    'coverage',
    'formencode',
    'Flask-SQLAlchemy',
    'flask-markdown',
    'blinker',
    ]

if __name__ == '__main__':
    setup(name='template',
          version='0.0',
          description='template-website',
          long_description=README,
          classifiers=[
              "Programming Language :: Python",
              "Framework :: Flask",
              "Topic :: Internet :: WWW/HTTP",
              "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
          ],
          author='',
          author_email='',
          url='',
          keywords='web wsgi flask',
          packages=find_packages(),
          include_package_data=True,
          zip_safe=False,
          tests_require=[
          ],
          test_suite='template',
          install_requires=requires,
      )
