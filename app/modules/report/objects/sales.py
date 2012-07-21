import app

from sqlalchemy import func

from app.modules.report.objects.pdf import TicketlistPDFReport

from app.modules.sales.objects.ticket import Ticket

class SalesReport(object):
    parameters = {'from': None, 'to': None}
    def getFilename(self):
        return 'sales-%(from)s-%(to)s' % self.parameters
    
    def generate(self, path):
        rep = TicketlistPDFReport(path, 'Sales Report',
                              None,
                              (self.parameters['from'], self.parameters['to']),
                              tickets=self.getTickets(self.parameters['from'], self.parameters['to']))

        return rep.build()

    def getTickets(self, from_date, to_date=None):
        session = app.database.session()
        query = session.query(Ticket)
        if to_date is None:
            query = query.filter(func.date(Ticket.date_close) == func.date(from_date))
        else:
            query = query.filter((func.date(Ticket.date_close) >= func.date(from_date)) & (func.date(Ticket.date_close) <= func.date(to_date)))
        query = query.order_by(Ticket.date_close.asc(), Ticket.date_open.asc(), Ticket.date_paid.desc())
        return query.all()
