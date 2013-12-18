import sys, os
import pkgutil, importlib

import cbpos
logger = cbpos.get_logger(__name__)

cbpos.config.set_default('mod', 'disabled_modules', list())
cbpos.config.set_default('mod', 'modules_path', list())

class BaseModuleLoader(object):
    """
    Abstract module loader from which all modules should have a subclass.
    Defines common actions that should take place when loading a module.
    """
    
    def ui_handler(self):
        """
        Defines a UI handler, an object responsible for setting up the UI
        and running it.
        It should allow modules to interact with it.
        Based on the configuration, the UI handler of the chosen module will be
        assigned to cbpos.ui when loading the modules.  
        """
        return None
    
    def load_models(self):
        """
        Loads the database models.
        """
        return []
    
    def test_models(self):
        """
        Create test models for the database.
        """
        pass
    
    def load_argparsers(self):
        """
        Add command line arguments and subparsers.
        """
        pass
    
    def menu(self):
        """
        Returns the menu structure [Roots, Children] Items corresponding to this module.
        """
        return [[], []]

    def actions(self):
        """
        Returns the actions structure.
        """
        return []
    
    def init(self):
        """
        Perform arbitrary initial tasks.
        Do NOT insert UI related code here.
        Connect to the appropriate dispatcher signals here instead.
        """
        return True
    
    def __repr__(self):
        return '<ModuleLoader %s>' % (self.base_name,)

class BaseModuleMetadata(object):
    """
    Abstract module metadata from which all modules should have a subclass.
    Defines attributes related to the module itself and its relation to
    the core and other modules.
    """
    has_ui_handler = False
    
    @property
    def base_name(self):
        raise NotImplementedError("Base name of module not defined")
    
    @property
    def version(self):
        raise NotImplementedError("Version of module not defined")
    
    @property
    def display_name(self):
        raise NotImplementedError("Display name of module not defined")
    
    @property
    def dependencies(self):
        raise NotImplementedError("Dependencies of module not defined")
    
    @property
    def config_defaults(self):
        raise NotImplementedError("Config defaults of module not defined")
    
    def __repr__(self):
        return '<ModuleMetadata %s>' % (self.base_name,)

class ModuleWrapper(object):
    """
    Wrapper around the actual installed module.
    Provides convenience functions for common tasks.
    """
    def __init__(self, package):
        self.package = package
        self.base_name = package[1]
        
        self.loader = None
        self.metadata = None
        self.disabled = False
        self.missing_dependency = False

    def load(self):
        """
        Load the module's package and initialize the ModuleLoader class. 
        """
        if self.disabled:
            raise TypeError("Cannot load a disabled module")
        self.top_module = importlib.import_module('cbpos.mod.'+self.base_name)
        if self.top_module is None:
            raise ImportError("Top module not found")
        
        try:
            self.loader = self.top_module.ModuleLoader()
        except AttributeError:
            raise ImportError("Module loader not found")
        
        try:
            self.metadata = self.top_module.ModuleMetadata()
        except AttributeError:
            raise ImportError("Module metadata not found")
        else:
            if self.metadata.base_name != self.base_name:
                raise ImportError("Module metadata basename for {} is incorrect".format(self.base_name))
        
        self.loader.base_name = self.base_name
        self.loader.metadata = self.metadata
        self.metadata.loader = self.loader
    
    def disable(self, missing_dependency=False):
        """
        Mark the module as disabled, specifying if it is conflicting with a missing dependency.
        """
        if self.disabled:
            return
        self.disabled = True
        self.missing_dependency = missing_dependency
        
        # Disable the import statements
        sys.modules['cbpos.mod.'+self.base_name] = None
    
    def set_config_defaults(self):
        """
        Set the config defaults for this module, from the metadata object.
        """
        if not self.metadata:
            raise ValueError('No metadata found. Cannot set config defaults.')
        for (section, options) in self.metadata.config_defaults:
            for opt, val in options.iteritems():
                cbpos.config.set_default(section, opt, val)
    
    @property
    def res_path(self):
        """
        Return the path to the module's resources.
        Only to be used when working with the modules themselves.
        Otherwise, use `cbpos.res.NAME('/path/to/resource')`.  
        """
        return getattr(cbpos.res, self.base_name)('')
    
    def __repr__(self):
        return '<ModuleWrapper %s>' % (self.base_name,)

class ModuleInitializer(object):
    def __init__(self):
        self.wrappers = {}
        self.missing = set()
        self.packages = []
        
        # Extract names of disabled modules from config
        self.disabled_names = cbpos.config['mod', 'disabled_modules']
        
        self.update_path(cbpos.config['mod', 'modules_path'])
    
    def run(self):
        """
        Load all modules, taking care of disabled and conflicting ones.
        """
        
        logger.debug('Loading modules...')
        logger.debug('Path ({}): {}'.format(len(self.path), repr(self.path)))
        
        try:
            if not sys.frozen: # if not frozen, sys.frozen raises AttributeError
                raise AttributeError
        except AttributeError:
            pass
        else:
            # Try to find the packages frozen in the executable with PyInstaller
            try:
                import pyi_importers
            except ImportError:
                logger.warn('App is frozen but pyi_importers is not available')
            else:
                # Find FrozenImporter object from sys.meta_path.
                importer = None
                for obj in sys.meta_path:
                    if isinstance(obj, pyi_importers.FrozenImporter):
                        importer = obj
                        break
    
                for name in importer.toc:
                    p = name.split('.')
                    if len(p) == 3 and p[0] == 'cbpos' and p[1] == 'mod':
                        self.packages.append((importer, p[2], True)) # The first and 3rd arguments are ignored
        
        # Package with names starting with '_' are ignored
        self.packages += [p for p in pkgutil.walk_packages(self.path) \
                          if not p[1].startswith('_') and p[2]]
        
        for pkg in self.packages:
            wrap = ModuleWrapper(pkg)
            
            self.wrappers[wrap.base_name] = wrap
            
            # Check if disabled
            if wrap.base_name in self.disabled_names:
                logger.debug('Module {} is disabled.'.format(wrap.base_name))
                wrap.disable()
                continue
            
            # Try to load the module
            logger.debug('Loading module {}...'.format(wrap.base_name))
            try:
                wrap.load()
            except ImportError:
                logger.warn('Invalid module {}.'.format(wrap.base_name))
                wrap.disable()
                continue
            except:
                logger.exception('Failed loading {}'.format(wrap.base_name))
                logger.warn('Invalid module {}.'.format(wrap.base_name))
                wrap.disable()
                continue
            
            wrap.set_config_defaults()
        
        self.check_dependencies()
        
        logger.debug('({}) modules found: {}'.format(
                    len(self.ordered_wrappers),
                    ', '.join(w.base_name for w in self.ordered_wrappers))
                     )
        
        logger.debug('({}) modules disabled: {}'.format(
                    len(self.disabled_wrappers),
                    ', '.join(m.base_name for m in self.disabled_wrappers))
                     )
        
        if len(self.missing) > 0:
            logger.warn('({}) modules disabled for missing dependencies: {}'.format(
                        len(self.missing),
                        ', '.join(name for name in self.missing))
                        )
    
    def check_dependencies(self):
        logger.debug('Checking module dependencies...')
        from collections import defaultdict
        conflicting = []
        self.dependent_on = defaultdict(list)
        
        for wrap in self.wrappers.itervalues():
            if wrap.disabled:
                continue
            for dep in wrap.metadata.dependencies:
                dep_base_name, dep_version = dep
                try:
                    dep_wrap = self.wrappers[dep_base_name]
                except KeyError:
                    # Module not found
                    conflicting.append(wrap)
                    logger.warn('Module {} requires module {} but it was not found'.format(wrap.base_name, dep_base_name))
                else:
                    if dep_wrap.disabled:
                        # Dependency disabled
                        conflicting.append(wrap)
                        logger.warn('Module {} requires module {} but it is disabled'.format(wrap.base_name, dep_base_name))
                    elif not self.version_match(dep_wrap, dep_version):
                        # Version does not match
                        conflicting.append(wrap)
                        logger.warn('Module {} requires module {} but its version does not match'.format(wrap.base_name, dep_base_name))
                    else:
                        self.dependent_on[dep_wrap.base_name].append(wrap)
        
        def resolve_conflict(wrap):
            if wrap.disabled:
                return
            wrap.disable(missing_dependency=True)
            self.missing.add(wrap.base_name)
            for w in self.dependent_on[wrap.base_name]:
                resolve_conflict(w)
        
        for wrap in conflicting:
            resolve_conflict(wrap)
        
        self.ordered_wrappers = self.sorted_wrappers(self.wrappers.itervalues())
        self.disabled_wrappers = [w for w in self.ordered_wrappers if w.disabled]
    
    def sorted_wrappers(self, wrappers):
        ordered = list(wrappers)
        for i in xrange(len(ordered)):
            for j in xrange(i+1, len(ordered)):
                if self.wrap_cmp(ordered[i], ordered[j]) > 0:
                    ordered[i], ordered[j] = ordered[j], ordered[i]
        return ordered
        # The built-in `sorted` does not do the job, it must use another algo
        # It happened that some were not properly ordered
        # So we have to use a custom algorithm to sort it
        #return sorted(self.wrappers.values(), cmp=self.wrap_cmp)
    
    def wrap_cmp(self, w1, w2):
        W1_COMES_FIRST, W2_COMES_FIRST, DOES_NOT_MATTER = -1, 1, 0
        
        if w1.disabled and w2.disabled:
            return DOES_NOT_MATTER
        elif w1.disabled:
            return W2_COMES_FIRST
        elif w2.disabled:
            return W1_COMES_FIRST
        
        elif w2 in self.dependent_on[w1.base_name] and w1 in self.dependent_on[w2.base_name]:
            return DOES_NOT_MATTER
        elif w2 in self.dependent_on[w1.base_name]:
            return W1_COMES_FIRST
        elif w1 in self.dependent_on[w2.base_name]:
            return W2_COMES_FIRST
        
        else:
            return DOES_NOT_MATTER
    
    def version_match(self, wrap, target_version):
        # Actual version
        a_parts = wrap.metadata.version.split('-', 2)
        if len(a_parts) == 2:
            a_version, a_build = a_parts
        else:
            a_version, a_build = a_parts[0], None
        a_version = a_version.split('.', 3)
        
        # Target version
        t_parts = target_version.split('-', 2)
        if len(t_parts) == 2:
            t_version, t_build = t_parts
        else:
            t_version, t_build = t_parts[0], None
        t_version = t_version.split('.', 3)
        
        # Build should match, if available
        if t_build != a_build:
            return False
        
        # All the target version parts should match
        for i, v in enumerate(t_version):
            try:
                if a_version[i] != v:
                    return False
            except IndexError:
                return False
        
        return True
    
    def update_path(self, values):
        """
        Insert the module paths from config by making sure:
         - there are no duplicates (set)
         - the custom paths exist
         - case-insensitive paths are taken into account
        """
        values = [] if values is None else values
        
        modules_path = set([os.path.normcase(os.path.realpath(p)) \
                            for p in values if p and os.path.exists(p)] + \
                           
                           [os.path.normcase(os.path.realpath(p)) \
                            for p in cbpos.mod.__path__])
        
        cbpos.mod.__path__ = list(modules_path)
        self.path = cbpos.mod.__path__
        return self.path

# Helper functions

initializer = None
def init():
    global initializer
    initializer = ModuleInitializer()
    return initializer.run()

def path():
    assert initializer is not None
    return initializer.path

def is_installed(module_name):
    return module_name in initializer.wrappers

def is_enabled(module_name):
    return is_installed(module_name) and \
        not initializer.wrappers[module_name].disabled

def all_wrappers():
    return initializer.ordered_wrappers

def by_name(module_name):
    return initializer.wrappers[module_name]

def disabled_wrappers():
    return [w for w in initializer.ordered_wrappers if w.disabled]

def enabled_wrappers():
    return [w for w in initializer.ordered_wrappers if not w.disabled]

def all_loaders():
    return [w.loader for w in initializer.ordered_wrappers if not w.disabled]

# TRANSLATORS

def init_translators(tr_builder):
    for mod in all_loaders():
        tr_builder.add(mod.base_name)

def init_resources(res):
    for mod in all_loaders():
        res.add(mod.base_name)

# ARGUMENT PARSERS
def load_argparsers():
    for mod in all_loaders():
        logger.debug('Adding command-line parsers for %s', mod.base_name)
        mod.load_argparsers()

# DATABASE EXTENSION

def load_database():
    """
    Load all the database models of every module so that they can be used with SQLAlchemy.
    """
    for mod in all_loaders():
        logger.debug('Loading DB models for %s', mod.base_name)
        models = mod.load_models()
        logger.debug('%d found.', len(models))

def config_database():
    """
    Clear and recreate the whole database.
    Note: Only the tables are changed, the database itself cannot be created or dropped.
    """
    logger.debug('Clearing database...')
    cbpos.database.clear()
    logger.debug('Creating database...')
    cbpos.database.create()

def config_test_database():
    """
    Insert the test database values of every module installed.
    """
    logger.debug('Adding test values to database...')
    for mod in all_loaders():
        logger.debug('Adding test values for %s', mod.base_name)
        mod.test_models()

# INTERFACE EXTENSION

def extend_interface(menu):
    """
    Load all menu extensions of every module, meaning all the root items and sub-items defined.
    Load all actions of every module.
    """
    roots = []
    items = []
    for mod in all_loaders():
        logger.debug('Loading menu for module %s...', mod.base_name)
        mod_roots, mod_items = mod.menu()
        roots.extend(mod_roots)
        items.extend(mod_items)
    
    [r.attach(menu) for r in roots]
    [i.attach(menu) for i in items]

    logger.debug('Menu roots (%d) and menu items (%d).', len(roots), len(items))

    for mod in all_loaders():
        logger.debug('Loading actions for module %s...', mod.base_name)
        [a.attach(menu) for a in mod.actions()]

    logger.debug('Actions (%d).', len(menu.actions))
