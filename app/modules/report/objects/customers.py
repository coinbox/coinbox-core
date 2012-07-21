import app

from sqlalchemy import func

from app.modules.report.objects.pdf import TicketlistPDFReport

from app.modules.sales.objects import Ticket

class CustomersReport(object):
    parameters = {'from': None, 'to': None, "show_card": None,
                  "show_cheque": None, "show_cash": None, "show_cheque": None,
                  "show_debt": None, "show_free": None}
    def getFilename(self):
        show = ("show_cash", "show_cheque", "show_card", "show_debt", "show_free")
        si = sum((self.parameters[s] or False)*(2**i) for i, s in enumerate(show))
        fmt = {"to": self.parameters["to"], "from": self.parameters["from"],
               "show": si, "customer": self.parameters["customer"].name}
        if fmt["to"] is not None:
            return 'customer-%(customer)s-%(from)s-%(to)s-%(show)s' % fmt
        else:
            return 'customer-%(customer)s-%(from)s-%(show)s' % fmt
    
    def generate(self, path):
        show = [s[5:] for s in ("show_cash", "show_cheque", "show_card", "show_debt", "show_free") \
                    if self.parameters[s]]
        # TODO currency is not taken in consideration
        rep = TicketlistPDFReport(path, 'Customer Report',
                              'Customer: %s' % (self.parameters['customer'].name,),
                              (self.parameters['from'], self.parameters['to']),
                              tickets=self.getTickets(self.parameters['customer'],
                                                self.parameters['from'], self.parameters['to'],
                                                show))

        return rep.build()

    def getTickets(self, c, _from, _to, show):
        session = app.database.session()
        query = session.query(Ticket).filter((Ticket.customer == c))
        if len(show) == 1:
            query = session.query(Ticket).filter(Ticket.payment_method == show)
        elif len(show) > 1:
            query = session.query(Ticket).filter(Ticket.payment_method.in_(show))
        if _to is None:
            query = query.filter(func.date(Ticket.date_close) == func.date(_from))
        else:
            query = query.filter(func.date(Ticket.date_close) >= func.date(_from) & func.date(Ticket.date_close) <= func.date(_to))
        query = query.order_by(Ticket.date_close.asc(), Ticket.date_open.asc(), Ticket.date_paid.desc())
        return query.all()
