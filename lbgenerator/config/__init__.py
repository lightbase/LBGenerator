# -*- coding: utf-8 -*-
# config

from sqlalchemy.schema import MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.engine import create_engine
from liblightbase.lbutils import object2json
from liblightbase.lbutils import json2object

def set_globals(**settings):

    global DB_URL
    global DB_NAME
    global POOL_SIZE
    global MAX_OVERFLOW
    global TMP_DIR
    global REQUESTS_TIMEOUT

    DB_URL = settings['sqlalchemy.url']
    DB_NAME = DB_URL.split('/')[-1]
    POOL_SIZE = int(settings['sqlalchemy.pool_size'])
    MAX_OVERFLOW = int(settings['sqlalchemy.max_overflow'])
    TMP_DIR = settings['storage.tmp_dir']
    REQUESTS_TIMEOUT = int(settings['requests.timeout'])

    global ENGINE
    global METADATA

    ENGINE = create_engine(DB_URL, pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW,
        json_serializer=object2json,
        json_deserializer=json2object
    )
    #ENGINE = create_engine(DB_URL, pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW, echo=True)
    METADATA = MetaData(ENGINE)

    global LOG_FILE
    global LOG_FORMAT
    #LOG_FILE = settings['log.file']
    #LOG_FORMAT = settings['log.format']
    LOG_FILE = '/var/log/lbgenerator.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    global AUTH_ENABLED
    global AUTH_INCLUDE_IP
    global ADMIN_USER
    global ADMIN_PASSWD

    AUTH_ENABLED = bool(int(settings['auth.enabled']))
    AUTH_INCLUDE_IP = bool(int(settings['auth.include_ip']))
    ADMIN_USER = settings['auth.admin_user']
    ADMIN_PASSWD = settings['auth.admin_passwd']

def create_new_engine():
    return create_engine(globals()['DB_URL'],
        pool_size=globals()['POOL_SIZE'],
        max_overflow=globals()['MAX_OVERFLOW'],
        json_serializer=object2json,
        json_deserializer=json2object)

def create_scoped_session(engine):
    return scoped_session(
        sessionmaker(bind=engine,
        autocommit=True))


