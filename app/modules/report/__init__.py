import app
from app.modules import Module

class ModuleLoader(Module):
    dependencies = ('base',)
    config = [['mod.report', {'report_dir': './res/report/pdf'}]]
    name = 'Generate PDF Reports for various modules'

    def menu(self):
        import app.modules
        
        items = []
        if app.modules.isAvailable('sales'):
            from app.modules.report.pages import SalesReportPage
            items.append({'parent': 'Reports', 'label': 'Sales', 'page': SalesReportPage,
                            'image': self.res('images/menu-sales.png')})
        
        if app.modules.isAvailable('customer'):
            from app.modules.report.pages import CustomersReportPage
            items.append({'parent': 'Reports', 'label': 'Customers', 'page': CustomersReportPage,
                            'image': self.res('images/menu-customers.png')})
        
        if app.modules.isAvailable('stock'):
            from app.modules.report.pages import StockReportPage
            from app.modules.report.pages import StockDiaryReportPage
            items.append({'parent': 'Reports', 'label': 'Stock', 'page': StockReportPage,
                            'image': self.res('images/menu-stock.png')})
            items.append({'parent': 'Reports', 'label': 'Stock Diary', 'page': StockDiaryReportPage,
                            'image': self.res('images/menu-diary.png')})
        
        if app.modules.isAvailable('user'):
            from app.modules.report.pages import UsersReportPage
            items.append({'parent': 'Reports', 'label': 'Users', 'page': UsersReportPage,
                            'image': self.res('images/menu-users.png')})
        
        return [[{'label': 'Reports', 'rel': -1, 'priority': 3, 'image': self.res('images/menu-root-reports.png')}],
                items]
