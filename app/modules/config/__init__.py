import app
from app.modules import Module

class ModuleLoader(Module):
    dependencies = ('base',)
    name = 'Configuration Interface Module'

    def menu(self):
        from app.modules.config.pages import MainConfigPage
            
        return [[],
                [{'parent': 'System', 'label': 'Configuration', 'page': MainConfigPage, 'image': self.res('images/menu-configuration.png')}]]
    
    def argparser(self):
        parser1 = app.subparsers.add_parser('config', description="Run qtPos database configuration")
        parser1.set_defaults(handle=self.load_config)
        
        parser2 = app.subparsers.add_parser('raw-config', description="Run qtPos raw configuration editor")
        parser2.set_defaults(handle=self.load_raw_config)

    def load_config(self, args):
        app.load_database(False)
        app.load_menu(False)
        app.log('LOG', 'Running configuration')
        
        # Prompt the user to change database configuration
        from .dialogs import DatabaseConfigDialog
        win = DatabaseConfigDialog()
        app.set_main_window(win)
        app.break_init()
    
    def load_raw_config(self, args):
        app.use_translation(False)
        app.load_database(False)
        app.load_menu(False)
        app.log('LOG', 'Running raw configuration')
        
        # Prompt the user to change database configuration
        from .dialogs import RawConfigDialog
        win = RawConfigDialog()
        app.set_main_window(win)
        app.break_init()