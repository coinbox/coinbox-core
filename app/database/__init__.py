from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import app
from .profile import get_used_profile

# Define default database configuration for different RDBMS's
app.config.set_default('db', 'used', 'default')
app.config.set_default('db', 'echo', '')

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
    return URL(**dict(get_used_profile()))

def clear():
    """
    Clear the database.
    Note: Drops all tables, does not drop database.
    """
    metadata = app.database.Base.metadata
    metadata.drop_all()

def create():
    """
    Create the database.
    Note: Creates all the tables, does not create the database itself.
    """
    metadata = app.database.Base.metadata
    metadata.create_all()

engine, Base, Session = None, None, None
def init():
    """
    Creates the SQLAlchemy engine, Session class and declarative base using the user's configuration.
    """
    global engine

    if engine is not None:
        app.log('WARN', 'Engine is not None')
        return
    
    app.log('LOG', 'Starting database')
    url = get_url()
    try:
        start(url)
    except:
        app.log('ERROR', 'Could not connect to database: %s' % (url,))
        return False
    else:
        return True

def start(url):
    global engine, Base, Session
    
    echo = bool(app.config['db', 'echo'])
    
    engine = create_engine(url, echo=echo)
    Base = declarative_base(bind=engine)
    Session = sessionmaker(bind=engine)

    # This is called to ensure an error is raised if connection failed
    engine.connect()
