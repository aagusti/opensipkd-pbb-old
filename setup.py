import os
import sys
import subprocess
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires=['pyramid >= 1.5.6, < 1.6a',
          'SQLAlchemy',
          'transaction',
          'pyramid_tm',
          'pyramid_debugtoolbar',
          'zope.sqlalchemy',          
          'waitress',
          'ziggurat-foundations >= 0.5, < 0.6',
          'colander',
          'deform >= 2.0a2',
          'pyramid_chameleon',
          'psycopg2',
          'alembic >= 0.3.4',
          'pyramid_beaker',
          'pytz',
          'paste',       
          'webhelpers',             
          'pyJasper',
          'sqlalchemy-datatables == 0.1.6',
          'simplejson',
         ]

if sys.argv[1:] and sys.argv[1] == 'develop-use-pip':
    bin_ = os.path.split(sys.executable)[0]
    pip = os.path.join(bin_, 'pip')
    for package in requires:
        cmd = [pip, 'install', package]
        subprocess.call(cmd)
    cmd = [sys.executable, sys.argv[0], 'develop']
    subprocess.call(cmd)
    sys.exit()

setup(name='opensipkd-pbb',
      version='0.0',
      description='opensipkd-pbb',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="opensipkd-pbb",
      entry_points = """\
      [paste.app_factory]
      main = pbb:main
      [console_scripts]
      initialize_opensipkd_pbb_db = pbb.scripts.initializedb:main      
      """,
      )
