__import__('pkg_resources').declare_namespace(__name__)

# Configuration access
import cbpos.configuration as configuration
config = configuration.Config('coinbox.cfg')

# Logging as specified in the configuration
import cbpos.logger as logger
logger.configure()
# Use the get_logger method in case the logging method ever changes
get_logger = logger.get_logger

# Load PyDispatcher for signals functionality
import pydispatch

# Resources system to access files for each module
from cbpos.resource import Resource
res = Resource()

# Load translation functionality
from cbpos.translator import TranslatorBuilder, DummyTranslatorBuilder
tr = None
locale = None

# Load extensible UI functionality
from cbpos.uihandler import BaseUIHandler
ui = None

# Load database access functionality
import cbpos.database as database

# Load module manipulation functionality
import cbpos.mod
import cbpos.modules as modules

# Menu items and actions
import cbpos.interface as interface
menu = interface.Menu()

# Command-line argument parsers
parser = None
subparsers = None
args = None
description = 'Launch coinbox POS'

# Load the core to the namespace
from cbpos.core import *
