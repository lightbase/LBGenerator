import os

from setuptools import setup, find_packages



here = os.path.abspath(os.path.dirname(__file__))
README = ''
CHANGES = ''

requires = [
    'alembic == 0.6.7',
    'Beaker == 1.11.0',
    'Mako == 1.1.3',
    'PasteDeploy == 2.1.1',
    'psycopg2 == 2.8.6',
    'pyramid == 1.5.1',
    'pyramid-beaker == 0.8',
    'pyramid-restler == 0.1a4',
    'repoze.lru == 0.7',
    'requests == 2.24.0',
    'SQLAlchemy == 0.9.4',
    'translationstring == 1.4',
    'venusian == 3.0.0',
    'voluptuous == 0.12.0',
    'waitress == 1.4.4',
    'WebOb == 1.6.3',
    'zope.deprecation == 4.1.1',
    'zope.interface == 4.1.1',
    'repoze.profile==2.2',
    'pympler==0.4.3'
]

'''
NOTE: Para versionamento usar "MAJOR.MINOR.REVISION.BUILDNUMBER"! By Questor
http://programmers.stackexchange.com/questions/24987/what-exactly-is-the-build-number-in-major-minor-buildnumber-revision
'''
setup(name='LBGenerator',
      version='0.8.0.0',
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
      """
      )
