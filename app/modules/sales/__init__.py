import app
from app.modules import Module

class ModuleLoader(Module):
    dependencies = ('base', 'currency', 'user', 'stock', 'customer')
    config = [['mod.sales', {'main_panel_sash_position': '0',
                             'main_panel_sash_mode': '1',
                             'main_panel_sash_split': '1'}]]
    name = 'Sales and Debt Support'

    def load(self):
        from app.modules.sales.objects.ticket import Ticket
        from app.modules.sales.objects.ticketline import TicketLine
        return [Ticket, TicketLine]

    def test(self):
        from app.modules.sales.objects.ticket import Ticket
        from app.modules.sales.objects.ticketline import TicketLine
    
        session = app.database.session()
    
        from app.modules.currency.objects.currency import Currency
        from app.modules.user.objects.user import User
        from app.modules.customer.objects.customer import Customer
    
        cu1 = session.query(Currency).filter_by(id=1).one()
        cu2 = session.query(Currency).filter_by(id=2).one()
        
        c1 = session.query(Customer).filter_by(id=1).one()
        
        u1 = session.query(User).filter_by(id=1).one()
    
        t1 = Ticket(discount=0, currency=cu1, user=u1, customer=None, comment='Test ticket 1')
        t2 = Ticket(discount=0.3, currency=cu2, user=u1, customer=c1, comment='Test ticket 2')
    
        from app.modules.stock.objects.product import Product
        
        p1 = session.query(Product).filter_by(id=1).one()
    
        tl1 = TicketLine(description='Ticketline 1-1', sell_price=2000, amount=1, discount=0, is_edited=False, ticket=t1, product=None)
        tl2 = TicketLine(description='Ticketline 1-2', sell_price=4500, amount=1, discount=0, is_edited=False, ticket=t1, product=None)
        tl3 = TicketLine(description='Ticketline 1-3 edited from p1', sell_price=5000, amount=2, discount=0, is_edited=True, ticket=t1, product=p1)
        tl4 = TicketLine(description='Ticketline 2-1', sell_price=5, amount=12, discount=0, is_edited=False, ticket=t2, product=None)
        tl5 = TicketLine(description='Ticketline 2-2 ewWeErRtTyYuUiIoOpP', sell_price=1.5, amount=12, discount=0, is_edited=True, ticket=t2, product=p1)
    
        [session.add(tl) for tl in (tl1, tl2, tl3, tl4, tl5)]
        session.commit()

    def menu(self):
        from app.modules.sales.pages import SalesPage
        #from app.modules.sales.pages import DebtsPage
            
        return [[],
                [{'parent': 'Main', 'label': 'Sales', 'page': SalesPage, 'rel': 0, 'priority': 5, 'image': self.res('images/menu-sales.png')},
                 #{'parent': 'Main', 'label': 'Debts', 'page': DebtsPage, 'rel': 0, 'priority': 4, 'image': self.res('images/menu-debts.png')}
                 ]]
