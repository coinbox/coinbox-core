import app
from app.modules import Module

class ModuleLoader(Module):
    name = 'Base Module'

    def menu(self):
        return [[{'label': 'Main', 'rel': 0, 'priority':5, 'image': self.res('images/menu-main.png')},
                 {'label': 'System', 'rel': -1, 'priority':4, 'image': self.res('images/menu-system.png')},
                 {'label': 'Administration', 'rel': -1, 'priority': 5, 'image': self.res('images/menu-administration.png')}],
                []]

    def config_pages(self):
        from app.modules.base.pages import MenuConfigPage, AppConfigPage, LocaleConfigPage
        return [AppConfigPage, MenuConfigPage, LocaleConfigPage]