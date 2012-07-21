import app
from app.modules import Module

class ModuleLoader(Module):
    dependencies = ('base',)
    config = [['mod.user', {'allow_empty_passwords': '1'}]]
    name = 'Authentication Support'

    def load(self):
        from app.modules.user.objects.permission import Permission, MenuRestriction
        from app.modules.user.objects.role import Role
        from app.modules.user.objects.user import User
        return [Permission, MenuRestriction, Role, User]

    def test(self):
        from app.modules.user.objects.permission import Permission, MenuRestriction
        from app.modules.user.objects.role import Role
        from app.modules.user.objects.user import User
    
        mr = lambda root, item: MenuRestriction(root=root, item=item)
    
        permissions_text = [
            ('common', 'Manage own user information', [mr('Administration', 'User')]),
            ('users', 'Manage users, permissions and roles.', [mr('Users', 'Users'), mr('Users', 'Roles'), mr('Users', 'Permissions')]),
            ('sales', 'Manage sales: tickets and orders.', [mr('Main', 'Sales'), mr('Main', 'Debts')]),
            ('cash', 'Manage cash register: close cash and manage payments.', []),
            ('stock', 'Manage products and categories in stock.', [mr('Stock', 'Products'), mr('Stock', 'Categories'), mr('Stock', 'Stock Diary')]),
            ('customers', 'Manage customers.', [mr('Customers', 'Customers'), mr('Customers', 'Groups')]),
            ('reports', 'View and print reports.', [mr('Reports', 'Sales'), mr('Reports', 'Customers'), mr('Reports', 'Stock'), mr('Reports', 'Stock Diary'), mr('Reports', 'Users')]),
            ('system', 'Edit system settings.', [mr('System', 'Configuration'), mr('System', 'Currencies')])]
        permissions = [Permission(name=p[0], description=p[1], menu_restrictions=p[2]) for p in permissions_text]
    
        admin_permissions = map(lambda p: permissions[p], range(len(permissions)))
        manager_permissions = map(lambda p: permissions[p], [0, 2, 3, 4, 5, 6])
        employee_permissions = map(lambda p: permissions[p], [0, 2])
    
        admin_role = Role(name='admin', permissions=admin_permissions)
        manager_role = Role(name='manager', permissions=manager_permissions)
        employee_role = Role(name='employee', permissions=employee_permissions)
    
        super_user = User(username='Super', password='super', hidden=True, super=True)
        admin_user = User(username='Admin', password='admin', role=admin_role)
        manager_user = User(username='Manager', password='manager', role=manager_role)
        employee_user = User(username='Employee', password='employee', role=employee_role)
    
        session = app.database.session()
        session.add(super_user)
        session.add(admin_user)
        session.add(manager_user)
        session.add(employee_user)
        session.commit()

    def menu(self):
        from app.modules.user.pages import UsersPage
        from app.modules.user.pages import RolesPage
        from app.modules.user.pages import PermissionsPage
        
        from app.modules.user.pages import IndividualUserPage
        
        return [[{'label': 'Users', 'rel': -2, 'priority': 3, 'image': self.res('images/menu-root-users.png')}],
                [{'parent': 'Users', 'label': 'Users', 'page': UsersPage, 'image': self.res('images/menu-users.png')},
                 {'parent': 'Users', 'label': 'Roles', 'page': RolesPage, 'image': self.res('images/menu-roles.png')},
                 {'parent': 'Users', 'label': 'Permissions', 'page': PermissionsPage, 'image': self.res('images/menu-permissions.png')},
                 {'parent': 'Administration', 'label': 'User', 'page': IndividualUserPage, 'image': self.res('images/menu-user.png')}]]

    def init(self):
        from PySide import QtGui
        from .dialogs import LoginDialog
        import app.modules.user.objects.user as user
        from app.modules.user.objects.user import User
        
        session = app.database.session()
        user_count = session.query(User).count()
        if user_count > 0:
            login = LoginDialog()
            app.set_main_window(login)
            return True
        else:
            user.current = User(username='_superuser_', password='_superuser_', hidden=True, super=True)
            session.add(user.current)
            session.commit()
            message = '''No user found. Creating Super User.
Create a normal user as soon as possible.
Use F3 to login as superuser again:
Username: _superuser_
Password: _superuser_
'''
            QtGui.QMessageBox.information(self, 'Login', message, QtGui.QMessageBox.Ok)
            return True

    def config_panels(self):
        from app.modules.user.pages import UserConfigPage 
        return [UserConfigPage]
