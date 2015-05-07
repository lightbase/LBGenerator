import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()

requires = [
	'liblightbase',
	'alembic == 0.6.7',
	'Beaker == 1.7.0.dev0',
	'Mako == 1.0.1',
	'PasteDeploy == 1.5.2',
	'psycopg2 == 2.5.3',
	'pyramid == 1.5.1',
	'pyramid-beaker == 0.8',
	'pyramid-restler == 0.1a4',
	'repoze.lru == 0.6',
	'requests == 2.3.0',
	'SQLAlchemy == 0.9.4',
	'translationstring == 1.1',
	'venusian == 1.0a8',
	'voluptuous == 0.8.7',
	'waitress == 0.8.9',
	'WebOb == 1.4',
	'zope.deprecation == 4.1.1',
	'zope.interface == 4.1.1'
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

