__all__ = ('run', 'terminate', 'use_translation', 'load_database', 'break_init',
           'set_ui_handler', 'load_menu')

import sys, os, argparse

from pydispatch import dispatcher
from babel import Locale, UnknownLocaleError
from sqlalchemy import exc

import cbpos
logger = cbpos.get_logger(__name__)

cbpos.config.set_default('app', 'fullscreen', False)
cbpos.config.set_default('app', 'first_run', True)
cbpos.config.set_default('app', 'ui_module', 'base')

def parse_args():
    cbpos.parser = argparse.ArgumentParser(description=cbpos.description)
    
    cbpos.subparsers = cbpos.parser.add_subparsers(dest='subparser_name')
    
    # This subparser does nothing, and just continues running Coinbox as if nothing was passed
    compat = cbpos.subparsers.add_parser('run', description="Run Coinbox")
    
    # Add the dummy 'run' subparser if none is given
    # TODO: That's a workaround because the version of argparse that ships with Python 2.7
    #       makes the subparser a required argument
    if len(sys.argv) == 1:
        logger.warn("We are appending the run subparser to the arguments...")
        sys.argv.append('run')
    
    # Load module-specific command-line arguments
    cbpos.modules.load_argparsers()
    
    cbpos.args = cbpos.parser.parse_args()
    
    if hasattr(cbpos.args, "handle"):
        ret = cbpos.args.handle(cbpos.args)
        return (ret is None or ret)
    return True

def init_translation(use=True):
    
    from cbpos.translator import TranslatorBuilder, DummyTranslatorBuilder
    
    def _babel_default():
        logger.debug('Babel is using default locale')
        
        # Use this language if no default can be found
        fallback_language = 'en_US'
        
        # Locale.default will raise an UnknownLocaleError if
        # the environment variables are not set or set wrong
        # This generally happens on Windows only
        # See: http://babel.edgewall.org/ticket/98 
        try:
            locale = Locale.default()
        except ValueError:
            logger.debug('Babel did not understand default locale')
            locale = Locale(fallback_language)
        except UnknownLocaleError:
            logger.debug('Babel does not support default locale')
            locale = Locale(fallback_language)
        else:
            cbpos.locale = locale
    
    if not use:
        tr_builder = DummyTranslatorBuilder()
        _babel_default()
        
        logger.info("Translation disabled.")
    else:
        # Read preferred settings from config file
        localedir = cbpos.config.env.locale_dir
        languages = cbpos.config['locale', 'languages']
        fallback = bool(cbpos.config['locale', 'fallback'])
        codeset = cbpos.config['locale', 'codeset']
        class_ = None # No need for a custom GNUTranslation class
        
        logger.debug("gettext is using [{languages}](codeset:{codeset}) for "
                     "translation with fallback={fallback} "
                     "in {directory}".format(
                    languages=','.join(languages) if languages else 'default',
                    codeset=codeset,
                    fallback=fallback,
                    directory=localedir)
                     )
        
        # Load gettext translations
        tr_builder = TranslatorBuilder(
            localedir=os.path.abspath(localedir),
            languages=None if not languages else languages,
            class_=class_,
            fallback=fallback,
            codeset=codeset
        )
        
        # Load Babel localization tools
        for lang in languages:
            try:
                locale = Locale.parse(lang)
            except ValueError:
                logger.debug('Babel does not understand locale %s', repr(lang))
            except UnknownLocaleError:
                logger.debug('Babel does not support locale %s', repr(lang))
            else:
                logger.debug('Babel is using locale %s', repr(lang))
                cbpos.locale = locale
                break
        else:
            _babel_default()
    
    cbpos.modules.init_translators(tr_builder)
    tr_builder.install()

def terminate(retcode=0):
    try:
        logger.info('Terminating application...')
    except:
        pass
    return sys.exit(retcode)

def run():
    """
    Main function to run the application.
    """
    global _ui_handler, _use_translation, _load_database, _load_menu, _break_init
    
    logger.info('Python: %s', sys.version)

    logger.debug('Importing database...')
    import cbpos.database

    logger.debug('Importing modules...')
    import cbpos.modules
    
    logger.debug('Running application...')
    
    cbpos.modules.init()
    cbpos.modules.init_resources(cbpos.res)
    
    if not parse_args():
        return
    
    # Check if it is the first run of the app
    if bool(cbpos.config['app', 'first_run']) or cbpos.config.empty():
        cbpos.config['app', 'first_run'] = False
        cbpos.first_run = True
    else:
        cbpos.first_run = False
    
    if cbpos.first_run:
        # Force configuration if configuration is empty.
        cbpos.config.save_defaults(overwrite=False)
        logger.info('First run. Saving configuration...')
    
    locale_use = bool(cbpos.config['locale', 'use'])
    init_translation(use=(_use_translation and locale_use))
    
    if _load_database:
        try:
            cbpos.database.init()
        except ImportError as e:
            # Either the required db backend is not installed
            logger.exception("Database initialization error")
            logger.fatal("Database connection failed. It seems this database backend is not installed.")
            return False
        except exc.SQLAlchemyError as e:
            # Or there is a database error (connection, etc.)
            logger.exception("Database initialization error")
            logger.fatal("Database connection failed. Check the configuration.")
            return False
        except Exception as e:
            # Or an unexpected error
            logger.exception("Database initialization error")
            return False
        # Load database objects of every module
        cbpos.modules.load_database()
    else:
        logger.debug('Did not load database.')
    
    if _load_menu:
        logger.debug('Extending menu...')
        # Load appropriate menu items from all the modules
        cbpos.modules.extend_interface(cbpos.menu)
        cbpos.menu.sort()
    else:
        logger.debug('Did not load menu.')
    
    if _break_init:
        logger.debug('Break init.')
    else:
        logger.debug('Initializing modules...')
        # Initiate every installed module
        for mod in cbpos.modules.all_loaders():
            logger.debug('Initializing module %s', mod.base_name)
            try:
                init = mod.init()
            except Exception as e:
                logger.exception('Initializing module %s failed.', mod.base_name)
                return False
            else:
                if not init:
                    logger.fatal('Initializing module %s failed.', mod.base_name)
                    return False
                elif _break_init:
                    break
    
    for mod in cbpos.modules.all_loaders():
        if mod.base_name == cbpos.config['app', 'ui_module']:
            set_ui_handler(mod.ui_handler())
            break
    
    if _ui_handler is None:
        logger.fatal('No UI Handler specified.')
        return False
    
    cbpos.ui = _ui_handler
    
    dispatcher.send(signal='ui-pre-init', sender='app')
    if not cbpos.ui.init():
        logger.fatal('Failed to initiate the UI Handler.')
        return False
    
    dispatcher.send(signal='ui-post-init', sender='app')
    
    return cbpos.ui.start()

_use_translation = True
_load_database = True
_load_menu = True
_break_init = False
_ui_handler = None

def use_translation(on=True):
    global _use_translation
    _use_translation = on

def load_database(on=True):
    global _load_database
    _load_database = on

def load_menu(on=True):
    global _load_menu
    _load_menu = on

def set_ui_handler(handler=None):
    global _ui_handler
    _ui_handler = handler

def break_init(on=True):
    global _break_init
    _break_init = on
