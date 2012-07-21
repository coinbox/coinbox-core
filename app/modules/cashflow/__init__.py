import app
from app.modules import Module

class ModuleLoader(Module):
    dependencies = ('base', 'currency')
    name = 'General Cash Flow Information'

    """
    def event_handler(self):
        self.bind_event(pos.EVT_ACTION, self.onPayment)
    """

    def load(self):
        from app.modules.cashflow.objects import CashFlow
        return [CashFlow]

    def menu(self):
        from app.modules.cashflow.pages import CashPage
        
        return [[],
                [{'parent': 'Main', 'label': 'Close Cash', 'page': CashPage}]]

    """
    def onPayment(self, evt):
        if evt.IsTargetted('cashflow'):
            action = evt.kwargs.get('action')
            if action not in ('income', 'payment'):
                return True
            
            from pos.modules.cashflow.objects.cashflow import CashFlow
            details = evt.kwargs.get('details', '')
            value = evt.kwargs.get('value', 0)
            currency = evt.kwargs.get('currency')
            user = evt.kwargs.get('user')
            
            if action == 'payment':
                value *= -1
            cf = CashFlow(source=evt.source, details=details, value=value, currency=currency, user=user)
            
            session = pos.database.session()
            session.add(cf)
            session.commit()
        return True
    """
