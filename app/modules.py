import sys, os
import pkgutil, imp, importlib

import logging
logger = logging.getLogger(__name__)

import app

app.config.set_default('mod', 'disabled_modules', '')
app.config.set_default('mod', 'modules_path', './app/mod')

class BaseModuleLoader(object):
    name = None
    dependencies = tuple()
    config = []
    version = 0
    
    def __init__(self, base_name):
        self.base_name = base_name
        if self.name is None:
            self.name = self.base_name.title()
        
        self.__bindings = {}
        
        for section, options in self.config:
            for opt, val in options.iteritems():
                app.config.set_default(section, opt, val)
        
        self.event_handler()
    
    def res(self, resource):
        return '%s/%s/%s' % (app.res_path(), self.base_name, resource)
    
    def load(self):
        return []
    
    def test(self):
        pass
    
    def menu(self):
        return [[], []]
    
    def argparser(self):
        pass
    
    def init(self):
        return True
    
    def event_handler(self):
        pass
    
    def bind_event(self, type_, callback):
        self.__bindings[type_] = callback
    
    def handle_event(self, evt):
        if evt.target is not None and self.base_name != self.type and \
            not (type(evt.type) in (list, tuple) and self.base_name in evt.type):
            return True
        try:
            callback = self.__bindings[evt.type]
        except KeyError:
            return True
        return callback(evt)
    
    def __lt__(self, mod):
        """
        Implements the '<' comparison operator.
        Used when sorting the list of modules, by dependencies.
        """
        return (self.base_name in mod.dependencies)
    
    def __repr__(self):
        return '<Module %s>' % (self.base_name,)
Module = BaseModuleLoader

class ModuleWrapper(object):
    """
    Wrapper around the actual installed module.
    Provides functions to make common tasks easier.
    """
    def __init__(self, package):
        self.package = package
        self.name = package[1]
        
        self.loader = None
        self.disabled = False
        self.forced_disable = False

    def load(self):
        """
        This will load the main module and initiate the ModuleLoader class 
        """
        if self.disabled:
            return False
        #modules_path = [os.path.abspath(path) for path in app.config['mod', 'modules_path'].split(':')]
        #if len(modules_path) == 1 and modules_path[0] == '':
        #    modules_path = os.path.join(os.path.dirname(__file__), 'mod')
        #loader_info = imp.find_module(self.name, modules_path)
        #self.top_module = imp.load_module('app.mod.'+self.name, *loader_info)
        self.top_module = importlib.import_module('app.mod.'+self.name)
        if self.top_module is None:
            return False
        try:
            self.loader = self.top_module.ModuleLoader(self.name)
        except AttributeError:
            return False
        setattr(importer, self.name, self.top_module)
        all_modules.append(self)
        return True
    
    def disable(self, missing_dependency=False):
        global disabled_modules, missing_modules
        self.disabled = True
        sys.modules['app.mod.'+self.name] = None
        if missing_dependency:
            self.forced_disable = True
            missing_modules.append(self)
        else:
            self.forced_disable = False
            disabled_modules.append(self)
    
    def uninstall(self):
        raise NotImplementedError, 'Uninstall a module is not yet supported.'
    
    def __repr__(self):
        return '<ModuleWrapper %s>' % (self.name, )

class ModuleImporter(object):
    pass

all_modules = []
disabled_modules = []
missing_modules = []
missing_dependencies = set()
module_loaders = []
importer = ModuleImporter()

def init():
    """
    Load all the modules installed (main and config).
    """
    global module_loaders
    
    disabled_str = app.config['mod', 'disabled_modules']
    disabled_names = disabled_str.split(',') if disabled_str != '' else []
    
    logger.debug('Loading modules...')
    modules_path = [os.path.abspath(path) for path in app.config['mod', 'modules_path'].split(':')]
    if len(modules_path) == 1 and modules_path[0] == '':
        modules_path = os.path.dirname(__file__)
    # Package with names starting with '_' are ignored
    packages = [p for p in pkgutil.walk_packages(modules_path) if not p[1].startswith('_') and p[2]]
    
    for pkg in packages:
        mod = ModuleWrapper(pkg)
        if mod.name in disabled_names:
            mod.disable()
            continue
        logger.debug('Loading module %s...' % (mod.name,))
        if not mod.load():
            logger.warn('Invalid module %s' % (mod.name,))
    logger.debug('(%d) modules found: %s' % (len(all_modules), ', '.join([m.name for m in all_modules])))
    if disabled_modules:
        logger.debug('(%d) modules disabled: %s' % (len(disabled_modules), ', '.join([m.name for m in disabled_modules])))
    check_dependencies()
    if missing_modules:
        logger.warn('(%d) modules disabled for missing dependencies: %s' % (len(missing_modules), ', '.join([m.name for m in missing_modules])))
    
    module_loaders = [mod.loader for mod in all_modules if not mod.disabled]
    module_loaders.sort()

def check_dependencies():
    logger.debug('Checking module dependencies...')
    to_remove = []
    module_names = set(mod.name for mod in all_modules)
    for mod in all_modules:
        missing = set(mod.loader.dependencies)-module_names
        if missing:
            missing_dependencies.update(missing)
            logger.warn('Missing dependencies for module %s: %s' % (mod.name, ', '.join(missing)))
            to_remove.append(mod)
    if not to_remove: return
    
    def iter_to_remove(remove_list, remove_set=set()):
        remove_set.update(remove_list)
        for mod in remove_list:
            used_in_set = set(m for m in all_modules if mod.name in m.loader.dependencies)
            iter_to_remove(used_in_set - remove_set, remove_set)
        return list(remove_set)
    
    [mod.disable(missing_dependency=True) for mod in iter_to_remove(to_remove)]

def is_installed(module_name):
    """
    Returns True if the module called module_name is installed.
    """
    for mod in all_modules:
        if module_name == mod.name:
            return True
    return False

def is_available(module_name):
    """
    Returns True if the module called module_name is installed and enabled.
    """
    for mod in module_loaders:
        if module_name == mod.base_name:
            return True
    return False

def all():
    """
    Returns a tuple of all the Module objects that are linked to all the actual modules installed.
    """
    return tuple(module_loaders)

def all_wrappers():
    """
    Returns a tuple of all the ModuleWrapper objects that are linked to all the actual modules installed.
    """
    return all_modules+disabled_modules+missing_modules

# TRANSLATORS

def init_translators(tr_builder):
    for mod in app.modules.all():
        tr_builder.add(mod.base_name)

# ARGUMENT PARSERS
def parse_args():
    for mod in app.modules.all():
        logger.debug('Parsing command-line arguments for %s' % (mod.base_name,))
        mod.argparser()

# DATABASE EXTENSION

def load_database():
    """
    Load all the database models of every module so that they can be used with SQLAlchemy.
    """
    for mod in module_loaders:
        logger.debug('Loading DB models for %s' % (mod.base_name,))
        models = mod.load()
        logger.debug('%d found.' % (len(models),))

def config_database():
    """
    Clear and recreate the whole database.
    Note: Only the tables are changed, the database itself cannot be created or dropped.
    """
    logger.debug('Clearing database...')
    app.database.clear()
    logger.debug('Creating database...')
    app.database.create()

def config_test_database():
    """
    Insert the test database values of every module installed.
    """
    logger.debug('Adding test values to database...')
    for mod in module_loaders:
        logger.debug('Adding test values for %s' % (mod.base_name,))
        mod.test()

# MENU EXTENSION

def extend_menu(menu):
    """
    Load all menu extensions of every module, meaning all the root items and sub-items defined.
    """
    from app.menu import MenuRoot, MenuItem
    roots = []
    items = []
    for mod in module_loaders:
        mod_roots, mod_items = mod.menu()
        roots.extend(mod_roots)
        items.extend(mod_items)

    for root in roots:
        MenuRoot(menu, **root)

    for item in items:
        MenuItem(menu, **item)
