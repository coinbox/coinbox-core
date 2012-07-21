import sys, os
import argparse
import PySide
from PySide import QtGui

import app

app.config.set_default('app', 'fullscreen', '')
app.config.set_default('app', 'first_run', '1')
app.config.set_default('app', 'log', '1')

app.log('LOG', 'Python: %s' % (sys.version,))
app.log('LOG', 'Platform: %s' % (sys.platform,))
app.log('LOG', 'PySide: %s' % (PySide.__version_info__,))

app.log('LOG', 'Creating menu')
import app.menu
app.menu.init()

app.log('LOG', 'Importing database')
import app.database

app.log('LOG', 'Importing modules')
import app.modules
app.modules.init()

def parse_args():
    # TODO: Careful!! We are using another version of argparse that does not ship with Python2.7
    # (I think it does with Python3.1) So there is a file called argparse.py
    # You will not be able to run the app without it.
    app.log('LOG', 'Parsing arguments. argparse is version ' + argparse.__version__)
    
    app.parser = argparse.ArgumentParser(description=app.description)
    
    app.subparsers = app.parser.add_subparsers(dest='subparser_name')
    
    # Load module-specific command-line arguments
    app.modules.parseArgs()
    
    app.args = app.parser.parse_args()
    
    if hasattr(app.args, "handle"):
        app.args.handle(app.args)

def init_translation(use=True):
    if not use:
        tr_builder = app.DummyTranslatorBuilder()
        
        app.log('LOG', "Translation disabled.")
    else:
        localedir = app.config['locale', 'localedir']
        languages = app.config['locale', 'languages']
        fallback = app.config['locale', 'fallback'] == '1'
        codeset = app.config['locale', 'codeset']
        class_ = None # No need for a custom GNUTranslation class
        
        app.log('LOG', "Using [%s](codeset:%s) for translation with fallback=%s in %s" % (languages, codeset, fallback, localedir))
        
        tr_builder = app.TranslatorBuilder(localedir=os.path.abspath(localedir),
                                           languages=None if languages == "" else languages.split(","),
                                           class_=class_,
                                           fallback=fallback,
                                           codeset=codeset)
    
    app.modules.init_translators(tr_builder)
    tr_builder.install()

def start():
    global _main_window
    app.log('LOG', 'Importing main window')
    from app.mainWindow import MainWindow
    
    app.config['app', 'first_run'] = ''
    _main_window = MainWindow()
    app.log('LOG', 'Loading menu')
    _main_window.loadMenu()
    
    fullscreen = (app.config['app', 'fullscreen'] != '')
    if fullscreen:
        _main_window.showFullScreen()
    else:
        _main_window.show()

def terminate():
    try:
        app.log('LOG', 'Terminating application')
    except:
        print 'Terminating application'

def run():
    """
    Main function to run the application.
    """
    global _main_window, _load_database, _break_init
    app.log('LOG', 'Running application')
    
    if app.config['app', 'first_run'] or app.config.empty():
        # Force configuration if configuration is empty.
        app.config.save_defaults(overwrite=False)
        app.log('LOG', 'First run, saving configuration')
    
    app.log('LOG', 'Creating application instance')
    app.main = QtGui.QApplication(sys.argv)
    
    parse_args()
    
    locale_use = (app.config['locale', 'use'] == '1')
    init_translation(use=(_use_translation and locale_use))
    
    app.log('LOG', 'Load database ' + repr(_load_database))
    if _load_database:
        if not app.database.init():
            return
        # Load database objects of every module
        app.modules.loadDB()
    
    app.log('LOG', 'Load menu ' + repr(_load_menu))
    if _load_menu:
        app.log('LOG', 'Extending menu')
        # Load appropriate menu items from all the modules
        app.modules.extendMenu(app.menu.main)
        app.menu.main.sort()
    
    app.log('LOG', 'Break Init ' + repr(_break_init))
    if not _break_init:
        app.log('LOG', 'Initializing modules')
        # Initiate every installed module
        for mod in app.modules.all():
            init = mod.init()
            if not init:
                app.log('LOG', 'Initializing module %s failed. Exit.' % (mod.base_name,))
                return False
            elif _break_init:
                break
    
    app.log('LOG', 'Main Window ' + repr(_main_window))
    if _main_window is None:
        start()
    else:
        _main_window.show()
    return app.main.exec_()

_use_translation = True
_load_database = True
_load_menu = True
_break_init = False
_main_window = None

def use_translation(on=True):
    global _use_translation
    _use_translation = on

def load_database(on=True):
    global _load_database
    _load_database = on

def load_menu(on=True):
    global _load_menu
    _load_menu = on

def set_main_window(win=None):
    global _main_window
    _main_window = win

def break_init(on=True):
    global _break_init
    _break_init = on
    
def res_path():
    return './res'