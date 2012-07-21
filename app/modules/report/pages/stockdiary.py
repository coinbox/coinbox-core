from .base import ReportPage
from app.modules.report.objects import StockDiaryReport

class StockDiaryReportPage(ReportPage):
    Report = StockDiaryReport
    def __init__(self):
        self.show_data_range = True
        super(StockDiaryReportPanel, self).__init__()
