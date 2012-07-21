import app
from app.modules import Module

class ModuleLoader(Module):
    dependencies = ('base',)
    name = 'Module Installer and Manager'

    def menu(self):
        from app.modules.installer.pages import ModulesPage
            
        return [[],
                [{'parent': 'System', 'label': 'Modules', 'page': ModulesPage, 'image': self.res('images/menu-modules.png')}]]

    def init(self):
        # Check for updates
        return True
