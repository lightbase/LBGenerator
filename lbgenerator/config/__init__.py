# -*- coding: utf-8 -*-
# config
import os
import tempfile
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

    # Add configuration as environment vars
    DB_URL = os.environ.get('SQLALCHEMY_URL', None)
    if DB_URL is None:
        DB_URL = settings['sqlalchemy.url']
    DB_NAME = DB_URL.split('/')[-1]

    POOL_SIZE = os.environ.get('SQLALCHEMY_POOL_SIZE', None)
    if POOL_SIZE is None:
        POOL_SIZE = int(settings['sqlalchemy.pool_size'])

    MAX_OVERFLOW = os.environ.get('SQLALCHEMY_MAX_OVERFLOW', None)
    if MAX_OVERFLOW is None:
        MAX_OVERFLOW = int(settings['sqlalchemy.max_overflow'])

    TMP_DIR = os.environ.get('STORAGE_TMP_DIR', None)
    if TMP_DIR is None:
        TMP_DIR = settings['storage.tmp_dir']

    # Eduardo: 20150114
    # Use system tmpdir in worst case scenario
    if not os.path.exists(TMP_DIR):
        TMP_DIR = tempfile.gettempdir()

    REQUESTS_TIMEOUT = os.environ.get('REQUESTS_TIMEOUT', None)
    if REQUESTS_TIMEOUT is None:
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

    AUTH_ENABLED = os.environ.get('AUTH_ENABLED', None)
    if AUTH_ENABLED is None:
        AUTH_ENABLED = bool(int(settings['auth.enabled']))

    AUTH_INCLUDE_IP = os.environ.get('AUTH_INCLUDE_IP', None)
    if AUTH_INCLUDE_IP is None:
        AUTH_INCLUDE_IP = bool(int(settings['auth.include_ip']))

    ADMIN_USER = os.environ.get('AUTH_ADMIN_USER', None)
    if ADMIN_USER is None:
        ADMIN_USER = settings['auth.admin_user']

    ADMIN_PASSWD = os.environ.get('AUTH_ADMIN_PASSWD', None)
    if ADMIN_PASSWD is None:
        ADMIN_PASSWD = settings['auth.admin_passwd']


def create_new_engine():
    return create_engine(
        globals()['DB_URL'],
        pool_size=globals()['POOL_SIZE'],
        max_overflow=globals()['MAX_OVERFLOW'],
        json_serializer=object2json,
        json_deserializer=json2object
    )


def create_scoped_session(engine):
    return scoped_session(
        sessionmaker(
            bind=engine,
            autocommit=True
        )
    )


