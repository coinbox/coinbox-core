from PySide import QtGui, QtCore

import app

import app.modules.user.objects.user as user
import app.modules.currency.objects.currency as currency
from app.modules.sales.objects import Ticket, TicketLine

from app.modules.stock.objects import Product
from app.modules.currency.objects import Currency

from app.modules.stock.widgets import ProductCatalog

from ..dialogs import EditDialog, PayDialog

class SalesPage(QtGui.QWidget):
    def __init__(self):
        super(SalesPage, self).__init__()

        self.tickets = QtGui.QComboBox()
        self.tickets.setEditable(False)
        self.tickets.activated[int].connect(self.onTicketChanged)

        ticketButtonBox = QtGui.QDialogButtonBox()
        
        self.newTicketBtn = ticketButtonBox.addButton("New", QtGui.QDialogButtonBox.ActionRole)
        self.newTicketBtn.pressed.connect(self.onNewTicketButton)
        
        self.closeTicketBtn = ticketButtonBox.addButton("Close", QtGui.QDialogButtonBox.ActionRole)
        self.closeTicketBtn.pressed.connect(self.onCloseTicketButton)
        
        self.cancelTicketBtn = ticketButtonBox.addButton("Cancel", QtGui.QDialogButtonBox.DestructiveRole)
        self.cancelTicketBtn.pressed.connect(self.onCancelTicketButton)
        
        topBar = QtGui.QHBoxLayout()
        topBar.addWidget(self.tickets, 0, QtCore.Qt.AlignLeft)
        topBar.addWidget(ticketButtonBox, 0, QtCore.Qt.AlignLeft)
        
        ticketlineButtonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        
        self.newTicketlineBtn = ticketlineButtonBox.addButton("New", QtGui.QDialogButtonBox.ActionRole)
        self.newTicketlineBtn.pressed.connect(self.onNewTicketlineButton)
        
        self.editTicketlineBtn = ticketlineButtonBox.addButton("Edit", QtGui.QDialogButtonBox.ActionRole)
        self.editTicketlineBtn.pressed.connect(self.onEditTicketlineButton)
        
        self.plusTicketlineBtn = ticketlineButtonBox.addButton("+", QtGui.QDialogButtonBox.ActionRole)
        self.plusTicketlineBtn.pressed.connect(self.onPlusTicketlineButton)
        
        self.minusTicketlineBtn = ticketlineButtonBox.addButton("-", QtGui.QDialogButtonBox.ActionRole)
        self.minusTicketlineBtn.pressed.connect(self.onMinusTicketlineButton)

        self.ticketTable = QtGui.QTableWidget()
        self.ticketTable.setColumnCount(5)
        self.ticketTable.verticalHeader().setVisible(False)
        self.ticketTable.setHorizontalHeaderLabels(("Description", "Price", "Amount", "Discount", "Total"))
        self.ticketTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.ticketTable.currentCellChanged.connect(self.onTicketlineItemChanged)
        self.ticketTable.cellDoubleClicked.connect(self.onTicketlineItemActivate)
        
        #TODO: the headers in the table are too big. the list won't appear completely, solution (?)
        # already using resizeColumns to contents in populate() after adding columns
        """
        header = self.ticketTable.horizontalHeader()
        font = QtGui.QFont()
        font.setPointSize(8) # or 6? it's too small 6...
        header.setFont(font)
        """
        
        self.code = QtGui.QLineEdit()
        self.code.returnPressed.connect(self.onCodeEnter)
        
        self.currency = QtGui.QComboBox()
        self.currency.setEditable(False)
        self.currency.activated[int].connect(self.onCurrencyChanged)
        
        self.customer = QtGui.QLineEdit()
        self.customer.setReadOnly(True)
        
        self.discount = QtGui.QDoubleSpinBox()
        self.discount.setRange(0, 100)
        self.discount.setSuffix('%')
        self.discount.valueChanged.connect(self.onDiscountValueChanged)
        
        self.total = QtGui.QLineEdit()
        self.total.setReadOnly(True)
        
        info = QtGui.QFormLayout()
        info.setSpacing(10)
        rows = (('Barcode', self.code),
                ('Currency', self.currency),
                ('Customer', self.customer),
                ('Discount', self.discount),
                ('Total', self.total)
                )
        [info.addRow(*row) for row in rows]
        
        #self.catalog = QtGui.QListWidget()
        self.catalog = ProductCatalog()
        
        layout = QtGui.QGridLayout()
        layout.addLayout(topBar, 0, 0, 1, 2, QtCore.Qt.AlignLeft)
        
        layout.addWidget(ticketlineButtonBox, 1, 0)
        layout.addWidget(self.ticketTable, 1, 1)
        
        layout.addLayout(info, 0, 2, 2, 1)
        
        layout.addWidget(self.catalog, 2, 0, 1, 3)
        
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)
        
        # TODO: re-implement sash
        position = int(app.config['mod.sales', 'main_panel_sash_position'])
        mode = int(app.config['mod.sales', 'main_panel_sash_mode'])
        split = bool(app.config['mod.sales', 'main_panel_sash_split'])
        print 'sash is', (position, mode, split)
        
        self.setCurrentTicket(None)
        
    def populate(self):
        session = app.database.session()
        
        tc = self.ticket.currency if self.ticket is not None else currency.get_default()
        items = session.query(Currency.display, Currency).all()
        self.currency.clear()
        for i, item in enumerate(items):
            self.currency.addItem(*item)
            if item[1] == tc:
                self.currency.setCurrentIndex(i)
        self.currency.setEnabled(True)

        ts = session.query(Ticket).filter(~Ticket.closed).all()
        self.tickets.clear()
        for i, t in enumerate(ts):
            label = 'Ticket #%s' % (t.id,)
            self.tickets.addItem(label, t)
        try:
            i = ts.index(self.ticket)
        except ValueError:
            i = -1
        self.tickets.setCurrentIndex(i)

        if self.ticket is None:
            self.customer.setText('[None]')
            self.discount.setValue(0)
            self.total.setText(tc.format(0))
            
            self.ticketTable.clearContents()
            self.ticketTable.setRowCount(0)
        else:
            c = self.ticket.customer
            self.customer.setText('[None]' if c is None else c.name)
            self.discount.setValue(self.ticket.discount*100.0)
            self.total.setText(tc.format(self.ticket.total))
            
            tls = self.ticket.ticketlines
            tc = self.ticket.currency
            self.ticketTable.setRowCount(len(tls))
            for row, tl in enumerate(tls):
                cols = (('* ' if tl.is_edited else '')+tl.description,
                 tc.format(tl.sell_price),
                 'x%d' % (tl.amount,),
                 '%d%%' % (tl.discount*100,),
                 tc.format(tl.total))
                for col, item_text in enumerate(cols):
                    table_item = QtGui.QTableWidgetItem(item_text)
                    table_item.setData(QtCore.Qt.UserRole+1, tl)
                    # Items are not enabled
                    table_item.setFlags(table_item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.ticketTable.setItem(row, col, table_item)
        self.ticketTable.resizeColumnsToContents()

    def setCurrentTicket(self, t):
        self.ticket = t
        
        enabled = t is not None
        self.enableTicketActions(enabled)
        self.currency.setEnabled(enabled)
        self.customer.setEnabled(enabled)
        self.discount.setEnabled(enabled)
        self.populate()
        
        self.enableTicketlineActions()

    def enableTicketActions(self, enable):
        self.newTicketBtn.setEnabled(True)
        self.closeTicketBtn.setEnabled(enable)
        self.cancelTicketBtn.setEnabled(enable)
        self.newTicketlineBtn.setEnabled(enable)

    def enableTicketlineActions(self):
        enable = (self.ticketTable.currentRow() != -1)
        self.plusTicketlineBtn.setEnabled(enable)
        self.minusTicketlineBtn.setEnabled(enable)
        self.editTicketlineBtn.setEnabled(enable)

    def _doCheckCurrentTicket(self):
        if self.ticket is None:
            QtGui.QMessageBox.warning(self, 'No ticket', 'Select a ticket.')
            return None
        else:
            return self.ticket

    def _doCheckCurrentTicketline(self):
        item = self.ticketTable.currentItem()
        if item is None:
            QtGui.QMessageBox.warning(self, 'No ticketline', 'Select a ticketline.')
            return None
        else:
            return item.data(QtCore.Qt.UserRole+1)

    def _doChangeAmount(self, inc):
        t = self._doCheckCurrentTicket()
        tl = self._doCheckCurrentTicketline()
        if t and tl:
            new_amount = tl.amount+inc
            if new_amount>0:
                p = tl.product
                if p is not None and p.in_stock and p.quantity<new_amount:
                    QtGui.QMessageBox.warning(self, 'Warning', 'Amount exceeds the product quantity in stock!')
                tl.update(amount=new_amount)
            else:
                tl.delete()
                self.enableTicketlineActions()
            self.populate()

    #####################
    #########   #########
    ##     onEvent     ##
    #########   #########
    #####################
    
    def onNewTicketButton(self):
        def_c = currency.get_default()
        t = Ticket()
        t.update(discount=0, user=user.current, currency=def_c)
        self.setCurrentTicket(t)
    
    def onCloseTicketButton(self):
        t = self._doCheckCurrentTicket()
        if t:
            dlg = PayDialog(t.total, t.currency, t.customer)
            dlg.exec_()
            if dlg.payment is not None:
                payment_method, paid = dlg.payment
                t.pay(str(payment_method), bool(paid))
                t.closed = True
                #evt = pos.Event('sales', pos.EVT_ACTION, action='ticket_paid', ticket=t, user=t.user)
                #evt2 = pos.Event('sales', pos.EVT_ACTION, 'cashflow', action='income', value=t.total,
                #                 currency=t.currency, user=t.user)
                #pos.event_queue.send(evt2)
                #pos.event_queue.send(evt)
                self.setCurrentTicket(None)
    
    def onCancelTicketButton(self):
        t = self._doCheckCurrentTicket()
        if t:
            t.delete()
            self.setCurrentTicket(None)
    
    def onTicketChanged(self, index):
        t = self.tickets.itemData(index)
        self.setCurrentTicket(t)
    
    def onTicketlineItemChanged(self, currentRow, currentColumn, previousRow, previousColumn):
        self.enableTicketlineActions()
    
    def onNewTicketlineButton(self):
        t = self._doCheckCurrentTicket()
        if t:
            data = {'description': '', 'amount': 1, 'sell_price': 0, 'discount': 0, 'ticket': t,
                    'product': None, 'is_edited': False}
            _init_data = data.copy()
            dlg = EditDialog(data)
            dlg.exec_()
            if data != _init_data:
                tl = TicketLine()
                tl.update(**data)
                self.populate()
    
    def onEditTicketlineButton(self):
        t = self._doCheckCurrentTicket()
        tl = self._doCheckCurrentTicketline()
        if t and tl:
            data = {'description': '', 'sell_price': 0, 'amount': 1, 'discount': 0, 'product': None, 'is_edited': False}
            tl.fillDict(data)
            _init_data = data.copy()
            dlg = EditDialog(data)
            dlg.exec_()
            if data != _init_data:
                tl.update(**data)
                self.populate()
    
    def onPlusTicketlineButton(self):
        self._doChangeAmount(+1)
    
    def onMinusTicketlineButton(self):
        self._doChangeAmount(-1)

    def OnSashChanged(self, event):
        event.Skip()
        position = self.splitter.GetSashPosition()
        mode = self.splitter.GetSplitMode()
        split = self.splitter.IsSplit()
        app.config['mod.sales', 'main_panel_sash_position'] = str(position)
        app.config['mod.sales', 'main_panel_sash_mode'] = str(mode)
        app.config['mod.sales', 'main_panel_sash_split'] = '1' if split else ''
        app.config.save()

    def onTicketlineItemActivate(self):
        self._doChangeAmount(+1)

    def onTicketlineItemRightClick(self):
        """This is not used!"""
        #TODO: should we use this? isn't it useless?
        # to use it, there is not signal itemRightClicked or similar
        # def mousePressEvent, view the coords, and self.rowAt/self.columnAt, then _doChangeAmount ?
        # notice that when right-clicking the cell is the selected (it is the current one...
        self._doChangeAmount(-1)

    ### Catalog Actions ###
    def onProductCatalogItemActivate(self):
        p = self.catalogBook.products.GetValue()
        if p is not None:
            t = self._doCheckCurrentTicket()
            if t:
                t.addLineFromProduct(p)
                self.populate()

    def onCustomerCatalogItemActivate(self):
        c = self.catalogBook.customers.GetValue()
        if c is not None:
            t = self._doCheckCurrentTicket()
            if t:
                t.update(customer=c, discount=c.discount)
                self.populate()

    ### Find Product Actions ###
    def onCurrencyChanged(self, index):
        t = self._doCheckCurrentTicket()
        if t:
            tc = t.currency
            index = self.currency.currentIndex()
            c = self.currency.itemData(index)
            if len(t.ticketlines) == 0:
                t.update(currency=c)
            else:
                reply = QtGui.QMessageBox.question(self, 'Change Currency', 'Change sell prices accordingly?')
                if reply == QtGui.QMessageBox.No:
                    t.update(currency=c)
                elif reply == QtGui.QMessageBox.Yes:
                    for tl in t.ticketlines:
                        tl.update(sell_price=currency.convert(tl.sell_price, tc, c))
                    t.update(currency=c)
            self.setCurrentTicket(t)
    
    def onDiscountValueChanged(self):
        value = self.discount.value()
        t = self._doCheckCurrentTicket()
        if t:
            t.update(discount=value/100.0)
        self.populate()
    
    def focusBarcode(self):
        self.code.selectAll()
        self.code.setFocus()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F3:
            self.focusBarcode()

    def onCodeEnter(self):
        t = self._doCheckCurrentTicket()
        if not t: return
        code = self.code.text()
        session = app.database.session()
        try:
            p = session.query(Product).filter_by(code=code).one()
        except:
            QtGui.QMessageBox.information(self, 'No match', 'Product with code %s not found.' % (code,))
            self.focusBarcode()
            # TODO: add the goTo functionality in the app package
            #app.goTo('Stock', 'Products')
        else:
            t.addLineFromProduct(p)
            self.populate()
            self.code.setText('')
