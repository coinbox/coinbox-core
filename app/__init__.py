from ._log import log

# Load the main interface for configuration access
import app.configuration as configuration
config = configuration.Config('coinbox.cfg')

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

from ._app import run, terminate, use_translation, load_database, break_init, set_main_window, load_menu, start, res_path