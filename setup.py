import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()

requires = [
    'pyramid == 1.5.4',
    'liblightbase',
    'pyramid_restler == 0.1a4',
    'sqlalchemy == 0.9.8',
    'psycopg2 == 2.6',
    'voluptuous == 0.8.7',
    'requests == 2.5.3',
    'pyramid_beaker == 0.8',
    'alembic == 0.7.4',
    'waitress == 0.8.9'
    ]


setup(name='LBGenerator',
      version='0.5',
      description='LBGenerator',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pylons",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
          ],
      author='Antony Carvalho',
      author_email='antony.carvalho@lightbase.com.br',
      url='',
      keywords='web pyramid pylons lightbase application',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="lbgenerator",
      entry_points = """\
      [paste.app_factory]
      main = lbgenerator:main
      """,
      )

