import app

from sqlalchemy import func

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, \
                                                 Paragraph, Spacer

from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

from app.modules.report.objects.pdf import PDFReport, stylesheet

from app.modules.stock.objects import DiaryEntry

def getDiaryEntries(_from, _to):
    session = app.database.session()
    query = session.query(DiaryEntry)
    if _to is None:
        query = query.filter(func.date(DiaryEntry.date) == func.date(_from))
    else:
        query = query.filter(func.date(DiaryEntry.date) >= func.date(_from) & func.date(DiaryEntry.date) <= func.date(_to))
    query = query.order_by(DiaryEntry.date.asc())
    return query.all()

class StockDiaryPDFReport(PDFReport):
    
    def _init_content(self):
        entries = getDiaryEntries(*self.date_range)
    
        headers = ('Operation ID', 'Date', 'Operation', 'Quantity', 'Product')
        data = []
        for de in entries:
            data.append([de.id,
                         de.date,
                         de.operation.title(),
                         de.quantity,
                         de.product.name])

        table = self.doTable(data=data, header=headers)

class StockDiaryReport(object):
    parameters = {'from': None, 'to': None}
    def getFilename(self):
        return 'stockdiary-%(from)s-%(to)s' % self.parameters
    
    def generate(self, path):
        rep = StockDiaryPDFReport(path, 'Stock Diary Report',
                         None,
                         (self.parameters['from'], self.parameters['to']),
                         (self.parameters['from'], self.parameters['to']))

        return rep.build()
