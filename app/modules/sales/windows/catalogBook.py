import wx

class CatalogBook(wx.Toolbook):
    def __init__(self, parent):
        wx.Toolbook.__init__(self, parent, -1, style=wx.BK_LEFT)

        # TODO change the imageList
        il = wx.ImageList(24,24, True)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_DIR_UP, size=(24, 24))
        il.Add(bmp)
        self.AssignImageList(il)
        
        self.products = ProductCatalog(self, show_only_in_stock=False)
        self.AddPage(imageId=0, page=self.products, text='Products')
        
        self.customers = CustomerCatalog(self)
        self.AddPage(imageId=0, page=self.customers, text='Customers')
