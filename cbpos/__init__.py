# Load the main interface for configuration access
import cbpos.configuration as configuration
config = configuration.Config('coinbox.cfg')

import cbpos.logger as logger
logger.configure()

import pydispatch

from cbpos.translator import TranslatorBuilder, DummyTranslatorBuilder
tr = None

ui = None

import cbpos.database as database
import cbpos.menu as menu
import cbpos.modules as modules

# Command-line argument parsers
parser = None
subparsers = None
args = None
description = 'Launch coinbox POS'

main = None

from cbpos.core import *