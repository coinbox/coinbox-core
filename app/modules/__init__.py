import app

app.config.set_default('mod', 'disabled_modules', '')

import sys, os
import pkgutil, importlib

class Module:
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

class ModuleWrapper:
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
        self.top_module = importlib.import_module('app.modules.'+self.name)
        if self.top_module is None:
            return False
        try:
            self.loader = self.top_module.ModuleLoader(self.name)
        except AttributeError:
            return False
        all_modules.append(self)
        return True
    
    def disable(self, missing_dependency=False):
        global disabled_modules, missing_modules
        self.disabled = True
        sys.modules['app.modules.'+self.name] = None
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

all_modules = []
disabled_modules = []
missing_modules = []
missing_dependencies = set()
module_loaders = []

def init():
    """
    Load all the modules installed (main and config).
    """
    global module_loaders
    
    disabled_str = app.config['mod', 'disabled_modules']
    disabled_names = disabled_str.split(',') if disabled_str != '' else []
    
    app.log('LOG', 'Loading modules')
    modules_path = os.path.dirname(__file__)
    # Package with names starting with '_' are ignored
    packages = [p for p in pkgutil.walk_packages([modules_path]) if not p[1].startswith('_') and p[2]]
    
    for pkg in packages:
        mod = ModuleWrapper(pkg)
        if mod.name in disabled_names:
            mod.disable()
            continue
        app.log('LOG', 'Loading module %s' % (mod.name,))
        if not mod.load():
            app.log('WARNING', 'Invalid module %s' % (mod.name,))
    app.log('LOG', '(%d) modules found: %s' % (len(all_modules), ', '.join([m.name for m in all_modules])))
    if disabled_modules:
        app.log('LOG', '(%d) modules disabled: %s' % (len(disabled_modules), ', '.join([m.name for m in disabled_modules])))
    _checkModuleDependencies()
    if missing_modules:
        app.log('LOG', '(%d) modules disabled for missing dependencies: %s' % (len(missing_modules), ', '.join([m.name for m in missing_modules])))
    
    module_loaders = [mod.loader for mod in all_modules if not mod.disabled]
    module_loaders.sort()

def _checkModuleDependencies():
    app.log('LOG', 'Checking module dependencies')
    to_remove = []
    module_names = set(mod.name for mod in all_modules)
    for mod in all_modules:
        missing = set(mod.loader.dependencies)-module_names
        if missing:
            missing_dependencies.update(missing)
            app.log('LOG', 'Missing dependencies for module %s: %s' % (mod.name, ', '.join(missing)))
            to_remove.append(mod)
    if not to_remove: return
    
    def iter_to_remove(remove_list, remove_set=set()):
        remove_set.update(remove_list)
        for mod in remove_list:
            used_in_set = set(m for m in all_modules if mod.name in m.loader.dependencies)
            iter_to_remove(used_in_set - remove_set, remove_set)
        return list(remove_set)
    
    [mod.disable(missing_dependency=True) for mod in iter_to_remove(to_remove)]

def isInstalled(module_name):
    """
    Returns True if the module called module_name is installed.
    """
    for mod in all_modules:
        if module_name == mod.name:
            return True
    return False

def isAvailable(module_name):
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
def parseArgs():
    for mod in app.modules.all():
        app.log('LOG', 'Parsing command-line arguments for %s' % (mod.base_name,))
        mod.argparser()

# DATABASE EXTENSION

def loadDB():
    """
    Load all the database objects of every module so that they can be used with SQLAlchemy.
    """
    for mod in module_loaders:
        app.log('LOG', 'Loading DB Objects for %s' % (mod.base_name,))
        objects = mod.load()
        app.log('LOG', '%d found' % (len(objects),))

def configDB():
    """
    Clear and recreate the whole database.
    Note: Only the tables are changed, the database itself cannot be created or dropped.
    """
    app.log('LOG', 'Clearing database')
    app.database.clear()
    app.log('LOG', 'Creating database')
    app.database.create()

def configTestDB():
    """
    Insert the test database values of every module installed.
    """
    app.log('LOG', 'Adding test values to database')
    for mod in module_loaders:
        app.log('LOG', 'Adding test values for %s' % (mod.base_name,))
        mod.test()

# MENU EXTENSION

def extendMenu(menu):
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
