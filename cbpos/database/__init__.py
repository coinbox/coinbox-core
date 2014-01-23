from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import cbpos
logger = cbpos.get_logger(__name__)

from .profile import Profile, ProfileNotFoundError
from .driver import Driver, DriverNotFoundError

# Define default database configuration for different RDBMS's
cbpos.config.set_default('db', 'used', 'default')
cbpos.config.set_default('db', 'echo', False)

_session = None
def session():
    """
    Returns a new session if none is present.
    TODO It is almost useless as it is always the same session that is returned. Check SQLAlchemy documentation in ORM>Session>FAQ for when to create a session.
    """
    global _session
    if _session is None:
        _session = Session()
    return _session

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

engine, Base, Session = None, None, None
def init():
    """
    Creates the SQLAlchemy engine, Session class and declarative base using the user's configuration.
    """
    global engine, Base, Session, _session

    if engine is not None:
        logger.warn('Engine is not None. Deleting and recreating one')
        del engine
        engine = None
    
    logger.debug('Starting database...')
    
    echo = bool(cbpos.config['db', 'echo'])
    url = get_url()
    
    engine = create_engine(url, echo=echo)
    Base = declarative_base(bind=engine)
    Session = sessionmaker(bind=engine)
    _session = None

    # This is called to ensure an error is raised if connection failed
    engine.connect()
