from .base import ReportPage
from app.modules.report.objects import StockReport

class StockReportPage(ReportPage):
    Report = StockReport
    def __init__(self):
        self.show_date_range = False
        super(StockReportPage, self).__init__()
