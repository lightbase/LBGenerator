import os
import tempfile

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.schema import MetaData
from sqlalchemy.engine import create_engine

from liblightbase.lbutils import object2json
from liblightbase.lbutils import json2object


def set_globals(**settings):
    """Seta variáveis globais com configurações adivindas de ambiente ou de 
    "ini".

    Args:
        settings (dict): Dicionário com configurações.
    """

    global DB_URL
    global DB_NAME
    global POOL_SIZE
    global MAX_OVERFLOW
    global TMP_DIR
    global REQUESTS_TIMEOUT
    global ENGINE
    global LBI_URL
    global ES_DEF_URL
    global METADATA
    global LOG_FILE
    global LOG_FORMAT
    global AUTH_ENABLED
    global AUTH_INCLUDE_IP
    global ADMIN_USER
    global ADMIN_PASSWD
    global LBRELACIONAL_URL

    # Add configuration as environment vars
    LBRELACIONAL_URL = os.environ.get('LBRELACIONAL_URL', None)
    if LBRELACIONAL_URL is None:
        LBRELACIONAL_URL = settings['lbrelacional.url']


    # NOTE: A forma como estamos convertendo booleanos (usando o método 
    # try_parse_to_bool) tá tosco, mas a forma como estar-se obtendo as 
    # configurações não está dentro do que fazemos regularmente em outras 
    # aplicações, conforme o exemplo...
    # 
    # "
    # config = ConfigParser.ConfigParser()
    # config.read('production.ini')
    # VALUE = config.getboolean('SECTION', 'value')
    # "
    # 
    # Pelo que entendi trata-se de uma condição advinda do Pyramid...
    # "Pyramid uses PasteDeploy in their infinite wisdom. ConfigParser will 
    # not work: it does not accept having . in the key names."
    # Ref.: http://stackoverflow.com/questions/10893628/how-can-i-get-the-ini-data-in-pyramid
    def try_parse_to_bool(value):
        """Converte um valor em string para boleano.

        Args:
            value (str): Valor em a ser covertido para boleano.

        Returns:
            bool: Retorno em booleano.
        """

        valid = {'y': True, 'yes': True, 't': True, 'true': True,
                 'on': True, '1': True, 'n': False, 'no': False,
                 'f': False, 'false': False, 'off': False, '0': False}

        if value is bool:
            return value

        if not isinstance(value, str):
            raise ValueError('Invalid literal for boolean! Not a string!')

        lower_value = value.lower()
        if lower_value in valid:
            return valid[lower_value]
        else:
            raise ValueError('Invalid literal for boolean: "%s"' % value)

    # NOTE: Add configuration as environment vars!
    DB_URL = os.environ.get('DATABASE_URL', None)
    if DB_URL is None:
        DB_URL = settings['sqlalchemy.url']
    DB_NAME = DB_URL.split('/')[-1]

    POOL_SIZE = os.environ.get('SQLALCHEMY_POOL_SIZE', None)
    if POOL_SIZE is None:
        POOL_SIZE = int(settings['sqlalchemy.pool_size'])
    else:
        POOL_SIZE = int(POOL_SIZE)

    MAX_OVERFLOW = os.environ.get('SQLALCHEMY_MAX_OVERFLOW', None)
    if MAX_OVERFLOW is None:
        MAX_OVERFLOW = int(settings['sqlalchemy.max_overflow'])
    else:
        MAX_OVERFLOW = int(MAX_OVERFLOW)

    TMP_DIR = os.environ.get('STORAGE_TMP_DIR', None)
    if TMP_DIR is None:
        TMP_DIR = settings['storage.tmp_dir']

    # NOTE: Use system tmpdir in worst case scenario!
    if not os.path.exists(TMP_DIR):
        TMP_DIR = tempfile.gettempdir()

    REQUESTS_TIMEOUT = os.environ.get('REQUESTS_TIMEOUT', None)
    if REQUESTS_TIMEOUT is None:
        REQUESTS_TIMEOUT = int(settings['requests.timeout'])
    else:
        REQUESTS_TIMEOUT = int(REQUESTS_TIMEOUT)

    ENGINE = create_engine(DB_URL, pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW,
        json_serializer=object2json,
        json_deserializer=json2object
    )

    # NOTE: URL to connect to the LBI - LBIndex to inform changes in the structure of a
    # base! By Questor
    LBI_URL = settings['lbindex_url']

    # NOTE: Base URL to ES - ElasticSearch. Will be used if "idx_exp" is true and
    # "idx_exp_url" is empty in a base "metadata"! By Questor
    ES_DEF_URL = settings['es_def_url']

    METADATA = MetaData(ENGINE)

    LOG_FILE = '/var/log/lbgenerator.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    AUTH_ENABLED = os.environ.get('AUTH_ENABLED', None)
    if AUTH_ENABLED is None:
        AUTH_ENABLED = bool(int(settings['auth.enabled']))
    else:
        AUTH_ENABLED = bool(int(AUTH_ENABLED))

    AUTH_INCLUDE_IP = os.environ.get('AUTH_INCLUDE_IP', None)
    if AUTH_INCLUDE_IP is None:
        AUTH_INCLUDE_IP = bool(int(settings['auth.include_ip']))
    else:
        AUTH_INCLUDE_IP = bool(int(AUTH_INCLUDE_IP))

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
