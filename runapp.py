import os

from paste.deploy import loadapp
from waitress import serve

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = loadapp('config:production.ini', relative_to='.')

    serve(app, host='0.0.0.0', port=port)