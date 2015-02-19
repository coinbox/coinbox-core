__all__ = ('CoreLoader',)

import sys, os, argparse

from pydispatch import dispatcher
from babel import Locale, UnknownLocaleError
from sqlalchemy import exc

import cbpos
logger = cbpos.get_logger(__name__)

cbpos.config.set_default('app', 'fullscreen', False)
cbpos.config.set_default('app', 'first_run', True)
cbpos.config.set_default('app', 'ui_module', 'base')

class CoreLoader(object):
    __autoload_translation = True
    __autoload_database = True
    __autoload_interface = True
    
    __loaded_resources = False
    __loaded_argparsers = False
    __loaded_translation = False
    __loaded_database = False
    __loaded_interface = False
    __loaded_modules = False
    
    # Use this language if no default can be found
    fallback_language = 'en_US'
    
    def load_resources(self, force=False):
        if self.__loaded_resources and not force:
            logger.debug('Trying to re-load resources.')
            return
        
        logger.debug('Loading resources...')
        
        for mod in cbpos.modules.all_loaders():
            cbpos.res.add(mod.base_name)
        
        self.__loaded_resources = True
    
    def load_argparsers(self, force=False):
        if self.__loaded_argparsers and not force:
            logger.debug('Trying to re-load argparsers.')
            return
        
        logger.debug('Loading argparsers...')
        
        cbpos.parser = argparse.ArgumentParser(description=cbpos.description)
        
        cbpos.subparsers = cbpos.parser.add_subparsers(dest='subparser_name')
        
        # This subparser does nothing, and just continues running Coinbox as if nothing was passed
        compat = cbpos.subparsers.add_parser('run', description="Run Coinbox")
        
        # This subparser sets cbpos.first_run to True to masquerade as a first run
        first = cbpos.subparsers.add_parser('first-run', description="Run Coinbox as first run")
        first.set_defaults(handle=self.__force_first_run)
        
        # Load module-specific command-line arguments
        for mod in cbpos.modules.all_loaders():
            logger.debug('Adding command-line parsers for %s', mod.base_name)
            mod.load_argparsers()
        
        self.__loaded_argparsers = True

    def __force_first_run(self, args):
        if not cbpos.first_run:
            cbpos.first_run = True

    def load_translation(self, force=False):
        if self.__loaded_translation and not force:
            logger.debug('Trying to re-load translation.')
            return False
        
        logger.debug('Loading translation...')
        
        if not cbpos.config['locale', 'use']:
            return self.load_unused_translation()
        
        from cbpos.translator import TranslatorBuilder, DummyTranslatorBuilder
        
        # Read preferred settings from config
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
                if locale is None:
                    logger.warn('Babel returned a null Locale!')
                    continue
                cbpos.locale = locale
                break
        else:
            self.__babel_default()
        
        for mod in cbpos.modules.all_loaders():
            tr_builder.add(mod.base_name)
        
        tr_builder.install()
        
        self.__loaded_translation = True
        return True
    
    def load_unused_translation(self, force=False):
        if self.__loaded_translation and not force:
            logger.debug('Trying to re-load (unused) translation.')
            return False
        
        logger.debug('Loading (unused) translation...')
        
        from cbpos.translator import TranslatorBuilder, DummyTranslatorBuilder
        
        tr_builder = DummyTranslatorBuilder()
        self.__babel_default()
        
        logger.info("Translation disabled.")
        
        for mod in cbpos.modules.all_loaders():
            tr_builder.add(mod.base_name)
        
        tr_builder.install()
        
        self.__loaded_translation = True
        return True

    def load_database(self, force=False):
        """
        Start the database and then load all the database models of every module
        so that they can be used with SQLAlchemy.
        """
        if self.__loaded_database and not force:
            logger.debug('Trying to re-load database.')
            return
        
        logger.debug('Loading database...')
        
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
        for mod in cbpos.modules.all_loaders():
            logger.debug('Loading DB models for %s', mod.base_name)
            models = mod.load_models()
        
        self.__loaded_database = True
        return True

    def load_interface(self, force=False):
        """
        Load all menu extensions of every module, meaning all the root items and sub-items defined.
        Load all actions of every module.
        """
        if self.__loaded_interface and not force:
            logger.debug('Trying to re-load interface.')
            return False
        
        logger.debug('Loading interface...')
        
        # Load interface from all the modules
        for mod in cbpos.modules.all_loaders():
            logger.debug('Loading interface for module %s...', mod.base_name)
            
            # Menu roots and items
            mod_roots, mod_items = mod.menu()
            [r.attach(cbpos.menu) for r in mod_roots]
            [i.attach(cbpos.menu) for i in mod_items]
            
            # Actions
            [a.attach(cbpos.menu) for a in mod.actions()]
        
        # Sort the menu according to priority rules
        cbpos.menu.sort()
        
        self.__loaded_interface = True
        return True
    
    def init_modules(self, force=False):
        if self.__loaded_modules and not force:
            logger.debug('Trying to re-initialize modules.')
            return False
        
        logger.debug('Initializing modules...')
        
        # Initialize every installed module
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
        
        self.__loaded_modules = True
        return True

    def run(self):
        """
        Main function to run the application.
        """
        logger.info('Python: %s', sys.version)
    
        logger.debug('Importing application components...')
        import cbpos.database
        import cbpos.modules
        
        logger.debug('Running application...')
        
        cbpos.modules.init()
        
        self.load_resources()
        
        self.load_argparsers()
        
        # Check if it is the first run of the app
        if bool(cbpos.config['app', 'first_run']) or cbpos.config.empty():
            cbpos.config['app', 'first_run'] = False
            cbpos.first_run = True
        else:
            cbpos.first_run = False
        
        # Force saving configuration if first run.
        if cbpos.first_run:
            cbpos.config.save_defaults(overwrite=False)
            logger.info('First run. Saving configuration...')
        
        # Parse the command-line arguments first
        if not self.parse_args():
            return
        
        # Load the UI Handler
        for mod in cbpos.modules.all_loaders():
            if mod.base_name == cbpos.config['app', 'ui_module']:
                cbpos.ui = mod.ui_handler()
                break
        else:
            logger.fatal('No UI Handler specified.')
            return False
        
        assert cbpos.ui is not None, 'UI Handler is None at a point where it should not be!'
        
        # Handle first run in the UI
        if cbpos.first_run:
            cbpos.ui.handle_first_run()
        
        if self.__autoload_translation:
            if not self.load_translation():
                return False
        else:
            self.load_unused_translation()
        
        if self.__autoload_database:
            if not self.load_database():
                return False
        else:
            logger.debug('Did not load database.')
        
        if self.__autoload_interface:
            if not self.load_interface():
                return False
        else:
            logger.debug('Did not load menu.')
        
        if not self.init_modules():
            return False
        
        dispatcher.send(signal='ui-pre-init', sender='app')
        
        if not cbpos.ui.init():
            logger.fatal('Failed to initialize the UI Handler.')
            return False
        
        dispatcher.send(signal='ui-post-init', sender='app')
        
        return cbpos.ui.start()

    def parse_args(self):
        
        # Add the dummy 'run' subparser if none is given
        # TODO: That's a workaround because the version of argparse that ships with Python 2.7
        #       makes the subparser a required argument
        if len(sys.argv) == 1:
            logger.warn("We are appending the run subparser to the arguments...")
            sys.argv.append('run')
        
        cbpos.args = cbpos.parser.parse_args()
        
        if hasattr(cbpos.args, "handle"):
            ret = cbpos.args.handle(cbpos.args)
            return (ret is None or ret)
        return True

    def __babel_default(self):
        logger.debug('Babel is using default locale')
        
        # Locale.default will raise an UnknownLocaleError if
        # the environment variables are not set or set wrong
        # This generally happens on Windows only
        # See: http://babel.edgewall.org/ticket/98 
        try:
            locale = Locale.default()
        except ValueError:
            logger.debug('Babel did not understand default locale')
            locale = Locale(self.fallback_language)
        except UnknownLocaleError:
            logger.debug('Babel does not support default locale')
            locale = Locale(self.fallback_language)
        else:
            if locale is None:
                logger.debug('Babel returned a default locale of None')
                locale = Locale(self.fallback_language)
            cbpos.locale = locale

    def terminate(self, retcode=0):
        try:
            logger.info('Terminating application...')
        except:
            pass
        return sys.exit(retcode)

    def autoload_translation(self, on=True):
        self.__autoload_translation = on
    
    def autoload_database(self, on=True):
        self.__autoload_database = on
    
    def autoload_interface(self, on=True):
        self.__autoload_interface = on
