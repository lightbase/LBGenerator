from pyramid.paster import get_app
application = get_app(
  '/srv/lightbase-neo/src/branches/1.0/LBGenerator/development.ini', 'main')

import lbgenerator.monitor
lbgenerator.monitor.start(interval=1.0)
