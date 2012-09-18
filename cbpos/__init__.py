import cbpos.logger as logger
import pydispatch

# Load the main interface for configuration access
import cbpos.configuration as configuration
config = configuration.Config('coinbox.cfg')

logger.configure()

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