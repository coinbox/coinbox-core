import app

from sqlalchemy import func

from app.modules.report.objects.pdf import TicketlistPDFReport

from app.modules.sales.objects import Ticket

class UsersReport(object):
    parameters = {'from': None, 'to': None, "show_card": None,
                  "show_cheque": None, "show_cash": None, "show_cheque": None,
                  "show_debt": None, "show_free": None}
    def getFilename(self):
        show = ("show_cash", "show_cheque", "show_card", "show_debt", "show_free")
        si = sum((self.parameters[s] or False)*(2**i) for i, s in enumerate(show))
        fmt = {"to": self.parameters["to"], "from": self.parameters["from"],
               "show": si, "customer": self.parameters["user"].username}
        if fmt["to"] is not None:
            return 'user-%(user)s-%(from)s-%(to)s-%(show)s' % fmt
        else:
            return 'user-%(user)s-%(from)s-%(show)s' % fmt
    
    def generate(self, path):
        show = [s[5:] for s in ("show_cash", "show_cheque", "show_card", "show_debt", "show_free") \
                    if self.parameters[s]]
        rep = TicketlistPDFReport(path, 'User Report',
                              'User: %s' % (self.parameters['user'].username,),
                              (self.parameters['from'], self.parameters['to']),
                              tickets=self.getTickets(self.parameters['user'], self.parameters['from'], self.parameters['to'], show))
        return rep.build()
    
    def getTickets(self, u, _from, _to, show):
        session = app.database.session()
        query = session.query(Ticket).filter((Ticket.user == u) & Ticket.payment_method.in_(show))
        if _to is None:
            query = query.filter(func.date(Ticket.date_close) == func.date(_from))
        else:
            query = query.filter(func.date(Ticket.date_close) >= func.date(_from) & func.date(Ticket.date_close) <= func.date(_to))
        query = query.order_by(Ticket.date_close.asc(), Ticket.date_open.asc(), Ticket.date_paid.desc())
        return query.all()