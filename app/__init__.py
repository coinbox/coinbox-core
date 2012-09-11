import app.logger as logger

# Load the main interface for configuration access
import app.configuration as configuration
config = configuration.Config('coinbox.cfg')

logger.configure()

from app.translator import TranslatorBuilder, DummyTranslatorBuilder
tr = None

import app.database as database
import app.menu as menu
import app.modules as modules

# Command-line argument parsers
parser = None
subparsers = None
args = None
description = 'Launch coinbox POS'

main = None

from app.core import *