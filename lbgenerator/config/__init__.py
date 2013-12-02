# -*- coding: utf-8 -*-
# config

from sqlalchemy.engine import create_engine
from sqlalchemy.schema import MetaData

def set_globals(**settings):

    global DB_URL
    global POOL_SIZE
    global MAX_OVERFLOW
    global TMP_DIR
    global REQUESTS_TIMEOUT

    DB_URL = settings['sqlalchemy.url']
    POOL_SIZE = int(settings['sqlalchemy.pool_size'])
    MAX_OVERFLOW = int(settings['sqlalchemy.max_overflow'])
    TMP_DIR = settings['storage.tmp_dir']
    REQUESTS_TIMEOUT = int(settings['requests.timeout'])

    global ENGINE
    global METADATA

    ENGINE = create_engine(DB_URL, pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW)
    METADATA = MetaData(ENGINE)

    global LOG_FILE
    global LOG_FORMAT
    #LOG_FILE = settings['log.file']
    #LOG_FORMAT = settings['log.format']
    LOG_FILE = '/var/log/lbgenerator.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

