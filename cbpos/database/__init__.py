from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import cbpos
logger = cbpos.get_logger(__name__)

from .profile import Profile, ProfileNotFoundError
from .driver import Driver, DriverNotFoundError

# Define default database configuration for different RDBMS's
cbpos.config.set_default('db', 'used', 'default')
cbpos.config.set_default('db', 'echo', False)

def get_url():
    """
    Return the URL to be used with engine creation based on configuration
    """
    used = Profile.get_used()
    return URL(**dict(used))

def clear():
    """
    Clear the database.
    Note: Drops all tables, does not drop database.
    """
    metadata = cbpos.database.Base.metadata
    metadata.drop_all()

def create():
    """
    Create the database.
    Note: Creates all the tables, does not create the database itself.
    """
    metadata = cbpos.database.Base.metadata
    metadata.create_all()

def fail_if_not_started():
    logger.warn('Trying to use the session while the database is not started.')
    raise TypeError('Cannot use session if database not started')

engine = None
session = fail_if_not_started
Base = declarative_base()
def init():
    """
    Creates the SQLAlchemy engine, Session class and declarative base using the user's configuration.
    """
    global engine, Base, session

    if engine is not None:
        logger.debug('Engine is not None. Start operation ignored.')
        return
    
    logger.debug('Starting database...')
    
    echo = bool(cbpos.config['db', 'echo'])
    url = get_url()
    
    engine = create_engine(url, echo=echo)
    Base.metadata.bind = engine
    session = scoped_session(sessionmaker(bind=engine))

    # This is called to ensure an error is raised if connection failed
    engine.connect()
