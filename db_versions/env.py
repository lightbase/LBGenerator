from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool, schema, create_engine
from logging.config import fileConfig

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

fileConfig(config.config_file_name)

DB_URL = config.get_main_option("sqlalchemy.url")
MAX_OVERFLOW = int(config.get_main_option("sqlalchemy.max_overflow"))
POOL_SIZE = int(config.get_main_option("sqlalchemy.pool_size"))

target_metadata = schema.MetaData(create_engine(DB_URL,
                                                pool_size=POOL_SIZE,
                                                max_overflow=MAX_OVERFLOW))

def run_migrations_offline():
    """
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata)

    with context.begin_transaction():

        # TODO: Não encontramos "run_migrations()" em nenhum local do código!
        # By Questor
        context.run_migrations()

def run_migrations_online():
    engine = engine_from_config(
                config.get_section(config.config_ini_section), prefix='sqlalchemy.')

    connection = engine.connect()
    context.configure(
                connection=connection,
                target_metadata=target_metadata
                )

    trans = connection.begin()
    try:

        # TODO: Não encontramos "run_migrations()" em nenhum local do código!
        # By Questor
        context.run_migrations()

        #trans.flush()
        trans.commit()
    except:
        trans.rollback()
        raise

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()