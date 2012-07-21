from .base import ReportPage

from app.modules.report.objects import SalesReport

class SalesReportPage(ReportPage):
    Report = SalesReport
    
    def __init__(self):
        self.show_date_range = True
        super(SalesReportPage, self).__init__()
