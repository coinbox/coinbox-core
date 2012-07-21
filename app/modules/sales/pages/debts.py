import wx

import pos

from pos.modules.sales.objects.ticket import Ticket

from pos.modules.customer.windows import CustomerCatalog

from ..dialogs import PayDialog

class DebtsPanel(wx.Panel):
    def _init_sizers(self):
        self.formSizer = wx.GridBagSizer(hgap=0, vgap=0)
        self.formSizer.Add(self.customerLbl, (0, 0))
        self.formSizer.Add(self.customerTxt, (0, 1))
        self.formSizer.Add(self.currentDebtLbl, (1, 0))
        self.formSizer.Add(self.currentDebtTxt, (1, 1))
        self.formSizer.Add(self.maxDebtLbl, (2, 0))
        self.formSizer.Add(self.maxDebtTxt, (2, 1))
        self.formSizer.AddGrowableCol(1, 1)

        self.controlSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.controlSizer.Add(self.payBtn, 0, flag=wx.ALIGN_RIGHT)
        
        self.mainSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.mainSizer.Add(self.customerList, 1, border=5, flag=wx.EXPAND | wx.ALL)
        self.mainSizer.AddSizer(self.formSizer, 1, border=5, flag=wx.EXPAND | wx.ALL)
        self.mainSizer.AddSizer(self.controlSizer, 0, border=5, flag=wx.EXPAND | wx.ALL)

        self.SetSizer(self.mainSizer)

    def _init_main(self):
        self.customerLbl = wx.StaticText(self, -1, label='Customer')
        self.customerTxt = wx.TextCtrl(self, -1, style=wx.TE_READONLY)

        self.currentDebtLbl = wx.StaticText(self, -1, label='Current Debt')
        self.currentDebtTxt = wx.TextCtrl(self, -1, style=wx.TE_READONLY)

        self.maxDebtLbl = wx.StaticText(self, -1, label='Max Debt')
        self.maxDebtTxt = wx.TextCtrl(self, -1, style=wx.TE_READONLY)
        
        self.customerList = CustomerCatalog(self)
        self.customerList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnCustomerCatalogItemActivate)

        self.payBtn = wx.Button(self, -1, label='Pay')
        self.payBtn.Bind(wx.EVT_BUTTON, self.OnPayButton)
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)

        self._init_main()
        self._init_sizers()
        
        self.setCustomer(None)

    def setCustomer(self, c):
        self.customer = c
        if c is not None:
            self.current_debt = self.customer.debt
            self.max_debt = self.customer.max_debt
            
            self.customerTxt.SetValue(self.customer.name)
            self.currentDebtTxt.SetValue(self.customer.currency.format(self.current_debt))
            self.maxDebtTxt.SetValue('[None]' if self.max_debt is None else self.customer.currency.format(self.max_debt))
            self.payBtn.Enable(True)
        else:
            self.current_debt = None
            self.max_debt = None
            
            self.customerTxt.SetValue('[None]')
            self.currentDebtTxt.SetValue('[None]')
            self.maxDebtTxt.SetValue('[None]')
            self.payBtn.Enable(False)

    def OnCustomerCatalogItemActivate(self, event):
        event.Skip()
        c = self.customerList.GetValue()
        self.setCustomer(c)

    def OnPayButton(self, event):
        event.Skip()
        dlg = PayDialog(None, self.current_debt, self.customer.currency, self.customer, disabled=['debt'])
        ret = dlg.ShowModal()
        if ret == wx.ID_OK:
            session = pos.database.session()
            unsettled_tickets = session.query(Ticket).filter(Ticket.customer == self.customer,
                                                             Ticket.payment_method == 'debt',
                                                             ~Ticket.paid).all()
            for t in unsettled_tickets:
                t.pay(*dlg.payment)
