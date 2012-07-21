import app
from app.modules import Module

class ModuleLoader(Module):
    dependencies = ('base',)
    config = [['mod.currency', {'default': ''}]]
    name = 'Multiple Currencies Support'

    def load(self):
        from app.modules.currency.objects.currency import Currency
        from app.modules.currency.objects.currencyunit import CurrencyUnit
        return [Currency, CurrencyUnit]

    def test(self):
        from app.modules.currency.objects.currency import Currency
        from app.modules.currency.objects.currencyunit import CurrencyUnit
        
        LL = Currency(name='Lebanese Lira', symbol='L.L.', value=1.0, decimal_places=0, digit_grouping=True)
        USD = Currency(name='U.S. Dollar', symbol='USD', value=1500, decimal_places=2, digit_grouping=True)
        EUR = Currency(name='Euro', symbol='EUR', value=2000, decimal_places=2, digit_grouping=True)
    
        ll_values = [250, 500, 1000, 5000, 10000, 20000, 50000, 100000]
        usd_values = [0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1, 2, 5, 10, 20, 50, 100]
        eur_values = [0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1, 2, 5, 20, 20, 50, 100, 500]
    
        [CurrencyUnit(value=v, currency=LL) for v in ll_values]
        [CurrencyUnit(value=v, currency=USD) for v in usd_values]
        [CurrencyUnit(value=v, currency=EUR) for v in eur_values]
    
        session = app.database.session()
        session.add(LL)
        session.add(USD)
        session.add(EUR)
        session.commit()

    def menu(self):
        from app.modules.currency.pages import CurrenciesPage
            
        return [[],
                [{'parent': 'System', 'label': 'Currencies', 'page': CurrenciesPage, 'image': self.res('images/menu-currencies.png')}]]

    def init(self):
        from PySide import QtGui
        from app.modules.currency.dialogs import CurrencyDialog
        from app.modules.currency.objects.currency import Currency
        
        session = app.database.session()
        currency_count = session.query(Currency).count()
        if currency_count == 0:
            win = CurrencyDialog()
            app.set_main_window(win)
            app.break_init()
            app.load_database(True)
            return True
        else:
            return True
    
    def config_pages(self):
        from app.modules.currency.pages import CurrencyConfigPage 
        return [CurrencyConfigPage]
