import app

from PySide import QtGui, QtCore

from app.modules.customer.objects import Customer

from .base import ReportPage
from app.modules.report.objects import CustomersReport
#from app.modules.report.dialogs import CustomerFilterDialog

class CustomersReportPage(ReportPage):
    Report = CustomersReport
    
    def __init__(self):
        self.show_date_range = True
        super(CustomersReportPage, self).__init__()

        """
        self.catalogList = CustomerCatalog(self.paramPanel)
        self.catalogList.SetValidator(ParamValidator(self, 'customer'))
        self.paramSizer.Add(self.catalogList, 0, flag=wx.EXPAND | wx.ALL)

        self.filterBtn = wx.Button(self.paramPanel, -1, label='Filter...')
        self.filterBtn.Bind(wx.EVT_BUTTON, self.OnFilterButton)
        self.paramSizer.Add(self.filterBtn, 0)
        """
    
    def initUI(self):
        self.customer = QtGui.QComboBox()
        self.customer.setEditable(False)
        
        layout = QtGui.QFormLayout()
        layout.setSpacing(10)
        
        layout.addRow("Customer", self.customer)
        
        self.populate()
        
        return layout
    
    def populate(self):
        session = app.database.session()
        customers = session.query(Customer.display, Customer).all()
        for customer in customers:
            self.customer.addItem(*customer)

    def updateParameters(self):
        i = self.customer.currentIndex()
        if i == -1:
            self.report.parameters["customer"] = None
        else:
            self.report.parameters["customer"] = self.customer.itemData(i)

    def onFilterButton(self):
        dlg = CustomerFilterDialog(self, ParamValidator)
        ret = dlg.ShowModal()
