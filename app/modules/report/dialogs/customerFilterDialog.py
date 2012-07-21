import wx

import pos

from pos.modules.currency.objects.currency import Currency

class CustomerFilterDialog(wx.Dialog):
    def __init_ctrls(self):
        self.okBtn = wx.Button(self, wx.ID_OK, label='OK')
        self.cancelBtn = wx.Button(self, wx.ID_CANCEL, label='Cancel')
    
    def __init_sizers(self):
        self.controlSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.controlSizer.Add(wx.Size(0, 0), 1, flag=wx.EXPAND | wx.ALL)
        self.controlSizer.Add(self.okBtn, 0, flag=wx.CENTER | wx.ALL)
        self.controlSizer.Add(wx.Size(0, 0), 1, flag=wx.EXPAND | wx.ALL)
        self.controlSizer.Add(self.cancelBtn, 0, flag=wx.CENTER | wx.ALL)
        self.controlSizer.Add(wx.Size(0, 0), 1, flag=wx.EXPAND | wx.ALL) 
        
        self.mainSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.mainSizer.AddSizer(self.paramSizer, 1, border=5, flag=wx.ALL | wx.EXPAND)
        self.mainSizer.AddSizer(self.controlSizer, 0, border=10, flag=wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self)
    
    def __init__(self, parent, validator):
        wx.Dialog.__init__(self, parent, -1,
              size=wx.Size(500, 500), title='Filter')

        self.paramSizer = wx.BoxSizer(orient=wx.VERTICAL)

        cbs = [('Cash', 'cash'),
               ('Cheque', 'cheque'),
               ('Card', 'card'),
               ('Debt', 'debt'),
               ('Free', 'free')]
        self.showSb = wx.StaticBox(self, -1, 'Show tickets paid')
        self.showSizer = wx.StaticBoxSizer(self.showSb, wx.VERTICAL)
        self.cbSizer = wx.GridSizer(cols=5)
        
        self.cbs = []
        for cb in cbs:
            self.cbs.append(wx.CheckBox(self, -1, label=cb[0], validator=validator(parent, 'show_'+cb[1])))
            self.cbSizer.Add(self.cbs[-1], 0, border=2, flag=wx.ALL)

        self.showSizer.Add(self.cbSizer, 1)
        self.paramSizer.Add(self.showSizer, 0)

        self.currencyChoice = wx.Choice(self, -1, validator=validator(parent, 'currency'))
        session = pos.database.session()
        currency_symbols = session.query(Currency.symbol).all()
        self.currencyChoice.SetItems(['[Any]']+[c[0] for c in currency_symbols])
        self.paramSizer.Add(self.currencyChoice, 0)

        self.__init_ctrls()
        self.__init_sizers()
