def bootstrap():
    # Configuration access
    import cbpos.configuration
    cbpos.config = cbpos.configuration.load()
    
    # Logging as specified in the configuration
    import cbpos.logger
    cbpos.logger.configure()
    # Use the get_logger method in case the logging method ever changes
    cbpos.get_logger = cbpos.logger.get_logger
    
    # Load PyDispatcher for signals functionality
    import pydispatch
    
    # Resources system to access files for each module
    from cbpos.resource import Resource
    cbpos.res = Resource()
    
    # Load translation functionality
    import cbpos.translator
    cbpos.tr = None
    cbpos.locale = None
    
    # Load extensible UI functionality
    import cbpos.uihandler
    cbpos.BaseUIHandler = cbpos.uihandler.BaseUIHandler
    cbpos.ui = None
    
    # Load database access functionality
    import cbpos.database
    
    # Load module manipulation functionality
    import cbmod
    import cbpos.modules
    
    # Menu items and actions
    import cbpos.interface
    cbpos.menu = cbpos.interface.Menu()
    
    # Command-line argument parsers
    cbpos.parser = None
    cbpos.subparsers = None
    cbpos.args = None
    cbpos.description = 'Launch coinbox POS'
    
    # First run flag, set when the application is run in `core.run`
    cbpos.first_run = False
    
    # Export all the functions defined here in the main namespace
    import cbpos.core
    for sym in cbpos.core.__all__:
        setattr(cbpos, sym, getattr(cbpos.core, sym))
