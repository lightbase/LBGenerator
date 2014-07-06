Install notes
=================================

LBGenerator was tested against following Python versions

* Python 3.2
* Python 3.3
* Python 3.4

Even though we didn't test it, we believe it can work on previous versions

* The following packages must be compiled to fave a full Lightbase Neo instance
	1. liblightbase
	2. LBGenerator
	3. LBApp
	
Dependencies
--------------

The following packages must be installed on Operating System (Debian based systems)
 
 * python-dev
 * libpq-dev
 * libffi-dev

Configuration
========================

Create pyramid configuration file according to your environment (development/production). Example .ini files are supplied with all the required parameters.

<pre>
cp development.ini-dist development.ini
</pre>

Change the following lines in your configuration file according to your environment

<pre>
sqlalchemy.url = postgresql://rest:rest@localhost/neolight
</pre>

Run alembic scripts to load base data into your PostgreSQL instance 

<pre>
alembic -c development.ini upgrade head
</pre>

Configure Apache + WSGI
--------------------

Configure your WSGI server and setup instance URL. In Debian you will need the following package:

* libapache2-mod-wsgi-py3

The following configuration will setup LBGenerator instance at /api

<pre>
# Use only 1 Python sub-interpreter.  Multiple sub-interpreters
# play badly with C extensions.
WSGIApplicationGroup %{GLOBAL}
WSGIPassAuthorization On
WSGIDaemonProcess lbgenerator user=www-data group=www-data threads=4 python-path=/home/eduardo/srv/lightbase-neo/lib/python3.4/site-packages
WSGIScriptAlias /api /home/eduardo/srv/lightbase-neo/src/LBGenerator/lbgenerator.wsgi

<Directory /home/eduardo/srv/lightbase-neo/src>
  WSGIProcessGroup lbgenerator
  Order allow,deny
  Allow from all
</Directory>
</pre>

Now you can use one of the supplied wsgi scripts:

<pre>
cp lbgenerator.wsgi-dist lbgenerator.wsgi
</pre>