import wx

import datetime

class DateRange(wx.PyPanel):
    def _init_sizers(self):
        self.dateSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.dateSizer.Add(self.fromLbl, 0, border=20, flag=wx.RIGHT)
        self.dateSizer.Add(self.fromDp, 0, border=10, flag=wx.EXPAND | wx.RIGHT)
        self.dateSizer.Add(self.toLbl, 0, border=10, flag=wx.RIGHT)
        self.dateSizer.Add(self.toDp, 0, border=10, flag=wx.EXPAND | wx.RIGHT)

        self.SetSizer(self.dateSizer)
        self.dateSizer.Fit(self)

    def _init_main(self):
        self.fromLbl = wx.StaticText(self, -1, label='From')
        self.fromDp = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN)

        self.toLbl = wx.StaticText(self, -1, label='To')
        self.toDp = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN | wx.DP_ALLOWNONE)

    def __init__(self, parent, id=-1, value=wx.EmptyString,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.TAB_TRAVERSAL|wx.NO_BORDER,
                 validator=wx.DefaultValidator,
                 name=wx.PanelNameStr):
        wx.Panel.__init__(self, parent, id=id, pos=pos,
                          size=size, style=style, name=name)

        self._init_main()
        self._init_sizers()

        if value != wx.EmptyString:
            self.SetValue(value)
        if validator is not wx.DefaultValidator:
            self.toDp.SetValidator(validator)
            self.fromDp.SetValidtor(validator)

    def SetValue(self, dt):
        wx_from_date = wx.DateTime()
        wx_from_date.Set(dt[0].day, dt[0].month, dt[0].year)
        self.fromDp.SetValue(wx_from_date)

        wx_to_date = wx.DateTime()
        if dt[1] is None:
            pass
        else:
            wx_to_date.Set(dt[1].day, dt[1].month, dt[1].year)
        self.toDp.SetValue(wx_to_date)

    def GetValue(self):
        wx_from_date = self.fromDp.GetValue()
        from_date = datetime.date.fromtimestamp(wx_from_date.GetTicks())
        
        wx_to_date = self.toDp.GetValue()
        to_date = None if not wx_to_date.IsValid() else datetime.date.fromtimestamp(wx_to_date.GetTicks())

        return (from_date, to_date)
