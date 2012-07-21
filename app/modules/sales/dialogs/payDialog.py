from PySide import QtGui, QtCore

import app

class PayDialog(QtGui.QDialog):
    
    def __init__(self, value, currency_, customer_, disabled=[]):
        super(PayDialog, self).__init__()

        self.value = value
        self.currency = currency_
        self.customer = customer_
        self.payment = None
        
        self.tabs = QtGui.QTabWidget()
        self.tabs.setTabPosition(QtGui.QTabWidget.West)
        self.tabs.setTabsClosable(False)
        self.tabs.setIconSize(QtCore.QSize(32, 32))
        self.tabs.setDocumentMode(True)
        
        self.due = QtGui.QLineEdit()
        self.due.setReadOnly(True)
        
        tab_bar = self.tabs.tabBar()
        selected = None
        panels = (CashPage(self),
                  ChequePage(self),
                  CardPage(self),
                  VoucherPage(self),
                  FreePage(self),
                  DebtPage(self)
                  )
        for p, page in enumerate(panels):
            self.tabs.addTab(page, page.icon, page.label)
            if not page.isAllowed() or page.payment[0] in disabled:
                tab_bar.setTabEnabled(p+1, False)
            elif selected is None:
                selected = p
                self.tabs.setCurrentIndex(p)

        buttonBox = QtGui.QDialogButtonBox()
        
        self.okBtn = buttonBox.addButton(QtGui.QDialogButtonBox.Ok)
        self.okBtn.pressed.connect(self.onOkButton)
        
        self.printBtn = buttonBox.addButton("Print", QtGui.QDialogButtonBox.ActionRole)
        self.printBtn.pressed.connect(self.onPrintButton)
        
        self.cancelBtn = buttonBox.addButton(QtGui.QDialogButtonBox.Cancel)
        self.cancelBtn.pressed.connect(self.onCancelButton)
        
        valueLayout = QtGui.QHBoxLayout()
        valueLayout.addWidget(QtGui.QLabel("Due Total"))
        valueLayout.addWidget(self.due)
        
        layout = QtGui.QVBoxLayout()
        layout.addLayout(valueLayout)
        layout.addWidget(self.tabs)
        layout.addWidget(buttonBox)
        
        self.setLayout(layout)
        
        self.due.setText(self.currency.format(self.value))

    def onPrintButton(self):
        QtGui.QMessageBox.information(self, "Print receipt", "Sorry, not available right now.")

    def onOkButton(self):
        page = self.tabs.currentWidget()
        if page.paymentOk():
            self.payment = page.payment
            self.close()
    
    def onCancelButton(self):
        self.payment = None
        self.close()

class CashPage(QtGui.QWidget):
    label = "Cash"
    icon = QtGui.QIcon('res/sales/images/pay-cash.png')
    payment = ("cash", True)
    
    def __init__(self, dialog):
        super(CashPage, self).__init__()

        self.dialog = dialog

        self.given = QtGui.QDoubleSpinBox()
        self.given.valueChanged.connect(self.onGivenValueChanged)
        
        self.change = QtGui.QLineEdit()
        self.change.setReadOnly(True)
        
        form = QtGui.QFormLayout()
        form.addRow("Given", self.given)
        form.addRow("Change", self.change)
        
        self.setLayout(form)
        
        self.givenValue = self.dialog.value
        self.changeValue = 0

        tc = self.dialog.currency
        self.given.setValue(self.givenValue)
        self.change.setText(tc.format(self.changeValue))

    def isAllowed(self):
        return True

    def paymentOk(self):
        if self.givenValue < self.dialog.value:
            tc = self.dialog.currency
            QtGui.QMessageBox.warning(self, 'Pay ticket', 'Not enough. %s remaining.' % (tc.format(-self.changeValue),))
            return False
        elif self.givenValue > self.dialog.value:
            tc = self.dialog.currency
            QtGui.QMessageBox.warning(self, 'Pay Ticket', 'Return change: %s.' % (tc.format(self.changeValue),))
            return True
        else:
            return True

    def onGivenValueChanged(self):
        try:
            self.givenValue = float(self.given.value())
        except:
            self.givenValue = 0
        self.changeValue = self.givenValue-self.dialog.value
        
        tc = self.dialog.currency
        self.change.setText(tc.format(self.changeValue))

class ChequePage(QtGui.QWidget):
    label = "Cheque"
    icon = QtGui.QIcon('res/sales/images/pay-cheque.png')
    payment = ("cheque", True)
    
    def __init__(self, dialog):
        super(ChequePage, self).__init__()

        self.dialog = dialog

    def isAllowed(self):
        return True

    def paymentOk(self):
        return True

class VoucherPage(QtGui.QWidget):
    label = "Voucher"
    icon = QtGui.QIcon('res/sales/images/pay-voucher.png')
    payment = ("voucher", True)
    
    def __init__(self, dialog):
        super(VoucherPage, self).__init__()

        self.dialog = dialog

        self.given = QtGui.QDoubleSpinBox()
        self.given.valueChanged.connect(self.onGivenValueChanged)
        
        self.change = QtGui.QLineEdit()
        self.change.setReadOnly(True)
        
        form = QtGui.QFormLayout()
        form.addRow("Voucher Value", self.given)
        form.addRow("Change", self.change)
        
        self.setLayout(form)
        
        self.givenValue = self.dialog.value
        self.changeValue = 0

        tc = self.dialog.currency
        self.given.setValue(self.givenValue)
        self.change.setText(tc.format(self.changeValue))

    def isAllowed(self):
        return True

    def paymentOk(self):
        if self.givenValue < self.dialog.value:
            tc = self.dialog.currency
            QtGui.QMessageBox.warning(self, 'Pay ticket', 'Not enough. %s remaining.' % (tc.format(-self.changeValue),))
            return False
        elif self.givenValue > self.dialog.value:
            tc = self.dialog.currency
            QtGui.QMessageBox.warning(self, 'Pay Ticket', 'Return change: %s.' % (tc.format(self.changeValue),))
            return True
        else:
            return True

    def onGivenValueChanged(self):
        try:
            self.givenValue = float(self.given.value())
        except:
            self.givenValue = 0
        self.changeValue = self.givenValue-self.dialog.value
        
        tc = self.dialog.currency
        self.change.setText(tc.format(self.changeValue))

class CardPage(QtGui.QWidget):
    label = "Card"
    icon = QtGui.QIcon('res/sales/images/pay-card.png')
    payment = ("card", True)
    
    def __init__(self, dialog):
        super(CardPage, self).__init__()

        self.dialog = dialog

    def isAllowed(self):
        return False

    def paymentOk(self):
        return False

class FreePage(QtGui.QWidget):
    label = "Free"
    icon = QtGui.QIcon('res/sales/images/pay-free.png')
    payment = ("free", False)
    
    def __init__(self, dialog):
        super(FreePage, self).__init__()

        self.dialog = dialog

    def isAllowed(self):
        return self.dialog.customer is not None

    def paymentOk(self):
        return True

class DebtPage(QtGui.QWidget):
    label = "Debt"
    icon = QtGui.QIcon('res/sales/images/pay-debt.png')
    payment = ("debt", False)
    
    def __init__(self, dialog):
        super(DebtPage, self).__init__()

        self.dialog = dialog

        self.debt = QtGui.QLineEdit()
        self.debt.setReadOnly(True)
        
        self.name = QtGui.QLineEdit()
        self.name.setReadOnly(True)
        
        self.maxDebt = QtGui.QLineEdit()
        self.maxDebt.setReadOnly(True)
        
        self.currentDebt = QtGui.QLineEdit()
        self.currentDebt.setReadOnly(True)
        
        form = QtGui.QFormLayout()
        rows = (("Debt", self.debt),
                ("Customer", self.name),
                ("Max Debt", self.maxDebt),
                ("Current Debt", self.currentDebt))
        
        [form.addRow(*row) for row in rows]
        
        self.setLayout(form)

        tc = self.dialog.currency
        self.debt.setText(tc.format(self.dialog.value))
        if self.dialog.customer is not None:
            cc = self.dialog.customer.currency
            self.name.setText(self.dialog.customer.name)
            self.maxDebt.setText(cc.format(self.dialog.customer.max_debt))
            self.currentDebt.setText(cc.format(self.dialog.customer.debt))

    def isAllowed(self):
        return self.dialog.customer is not None

    def paymentOk(self):
        if self.dialog.customer is not None:
            return True
