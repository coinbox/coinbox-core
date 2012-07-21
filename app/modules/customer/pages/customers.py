from PySide import QtCore, QtGui

import app

import app.modules.currency.objects.currency as currency
from app.modules.currency.objects.currency import Currency

from app.modules.customer.objects.customer import Customer
from app.modules.customer.objects.group import CustomerGroup
from app.modules.customer.objects.contact import CustomerContact
from app.modules.customer.objects.address import CustomerAddress

from app.modules.base.pages import FormPage

class CustomersPage(FormPage):
    itemClass = Customer
    def fields(self):
        discount = QtGui.QDoubleSpinBox()
        discount.setRange(0, 100)
        
        max_debt = QtGui.QDoubleSpinBox()
        max_debt.setMinimum(0)
        
        groups = QtGui.QTreeWidget()
        groups.setHeaderHidden(True)
        
        return [("name", "Name", QtGui.QLineEdit(), ""),
                ("code", "Code", QtGui.QLineEdit(), ""),
                ("first_name", "First Name", QtGui.QLineEdit(), ""),
                ("last_name", "Last Name", QtGui.QLineEdit(), ""),
                ("discount", "General Discount", discount, 0),
                ("max_debt", "Maximum Debt", max_debt, 0),
                ("currency", "Preferred Currency", QtGui.QComboBox(), currency.get_default()),
                ("groups", "Groups", groups, []),
                ("comment", "Comment", QtGui.QTextEdit(), ""),
                ("contacts", "Contacts", ContactsWidget(), []),
                ("addresses", "Addresses", AddressesWidget(), [])
                ]
    
    def items(self):
        session = app.database.session()
        items = session.query(Customer.display, Customer).all()
        return items
    
    def canDeleteItem(self, item):
        return True
    
    def canEditItem(self, item):
        return True
    
    def canAddItem(self):
        return True
    
    def getDataFromControl(self, field):
        if field in ('name', 'code', 'first_name', 'last_name'):
            data = self.f[field].text()
        elif field == 'comment':
            data = self.f[field].toPlainText()
        elif field == 'discount':
            data = self.f[field].value()/100.0
        elif field == 'max_debt':
            data = self.f[field].value()
            data = data if data>0 else None
        elif field == 'currency':
            selected_index = self.f[field].currentIndex()
            if selected_index == -1:
                data = None
            else:
                data = self.f[field].itemData(selected_index)
        elif field == 'groups':
            data = []
            for i in xrange(self.f[field].topLevelItemCount()):
                root = self.f[field].topLevelItem(i)
                if root.checkState(0) == QtCore.Qt.Checked:
                    item = root.data(0, QtCore.Qt.UserRole+1)
                    data.append(item)
        elif field == 'contacts':
            tmps = self.f[field].contacts()
            data = []
            for tmp in tmps:
                if tmp.contact is None:
                    data.append(CustomerContact(name=tmp.name, value=tmp.value))
                else:
                    tmp.contact.name = tmp.name
                    tmp.contact.value = tmp.value
                    data.append(tmp.contact)
        elif field == 'addresses':
            tmps = self.f[field].addresses()
            data = []
            for tmp in tmps:
                if tmp.address is None:
                    data.append(CustomerAddress(country=tmp.country, region=tmp.region, \
                                                city=tmp.city, details=tmp.details))
                else:
                    tmp.address.country = tmp.country
                    tmp.address.region = tmp.region
                    tmp.address.city = tmp.city
                    tmp.address.details = tmp.details
                    data.append(tmp.address)
        return (field, data)
    
    def setDataOnControl(self, field, data):
        if field in ('name', 'code', 'first_name', 'last_name', 'comment'):
            self.f[field].setText(data if data is not None else '')
        elif field == 'discount':
            self.f[field].setValue(data*100.0)
        elif field == 'max_debt':
            self.f[field].setValue(data if data is not None else 0)
        elif field == 'currency':
            session = app.database.session()
            items = session.query(Currency.display, Currency).all()
            self.f[field].clear()
            for i, item in enumerate(items):
                self.f[field].addItem(*item)
                if item[1] == data:
                    self.f[field].setCurrentIndex(i+1)
        elif field == 'groups':
            session = app.database.session()
            items = session.query(CustomerGroup.display, CustomerGroup).all()
            self.f[field].clear()
            for item in items:
                root = QtGui.QTreeWidgetItem(self.f[field], [item[0]])
                root.setData(0, QtCore.Qt.UserRole+1, item[1])
                if item[1] in data:
                    root.setCheckState(0, QtCore.Qt.Checked)
                else:
                    root.setCheckState(0, QtCore.Qt.Unchecked)
        elif field == 'contacts':
            self.f[field].setContacts(data)
        elif field == 'addresses':
            self.f[field].setAddresses(data)
    
    def getDataFromItem(self, field, item):
        return getattr(item, field)

class ContactsWidget(QtGui.QWidget):
    
    def __init__(self):
        super(ContactsWidget, self).__init__()
        
        self.nameList = ('email', 'phone', 'mobile', 'fax')
        
        self.__tmp = []
        
        self.addBtn = QtGui.QPushButton('Add')
        self.addBtn.clicked.connect(self.onAddButton)
        
        self.rows = QtGui.QVBoxLayout()
        self.rows.setSpacing(5)
        
        self.rows.addWidget(self.addBtn)
        
        self.setLayout(self.rows)
    
    def addRow(self, contact=None):
        nameCb = QtGui.QComboBox()
        nameCb.addItems(self.nameList)
        
        valueTxt = QtGui.QLineEdit()
        
        tmp = TempContact(contact)
        self.__tmp.append(tmp)
        
        removeBtn = QtGui.QPushButton('-')
        removeBtn.clicked.connect(lambda tmp=tmp: self.onRemoveButton(tmp))
        
        nameCb.setCurrentIndex(self.nameList.index(tmp.name))
        valueTxt.setText(tmp.value)
        
        tmp.layout = QtGui.QHBoxLayout()
        tmp.layout.addWidget(nameCb)
        tmp.layout.addWidget(valueTxt)
        tmp.layout.addWidget(removeBtn)
        self.rows.addLayout(tmp.layout)
    
    def onAddButton(self):
        self.addRow(None)
    
    def onRemoveButton(self, tmp):
        tmp.removed = True
        self.rows.removeItem(tmp.layout)
    
    def setContacts(self, contacts):
        for tmp in self.__tmp:
            self.rows.removeItem(tmp.layout)
        self.__tmp = []
        [self.addRow(c) for c in contacts]
    
    def contacts(self):
        for tmp in self.__tmp:
            tmp.name = tmp.layout.itemAt(0).widget().currentText()
            tmp.value = tmp.layout.itemAt(1).widget().text()
        return [tmp for tmp in self.__tmp if not tmp.removed]

class TempContact(object):
    name = 'email'
    value = ''
    contact = None
    layout = None
    removed = False
    def __init__(self, contact=None):
        self.contact = contact
        if contact is not None:
            self.name = contact.name
            self.value = contact.value

class AddressesWidget(QtGui.QWidget):
    
    def __init__(self):
        super(AddressesWidget, self).__init__()
        
        self.__tmp = []
        
        self.list = QtGui.QComboBox()
        self.list.currentIndexChanged.connect(self.onAddressChanged)
        
        self.addBtn = QtGui.QPushButton('Add')
        self.addBtn.clicked.connect(self.onAddButton)
        
        self.removeBtn = QtGui.QPushButton('Remove')
        self.removeBtn.clicked.connect(self.onRemoveButton)
        
        self.country = QtGui.QLineEdit()
        self.region = QtGui.QLineEdit()
        self.city = QtGui.QLineEdit()
        self.details = QtGui.QTextEdit()
        
        self.form = QtGui.QFormLayout()
        self.form.setSpacing(5)
        
        rows = [[self.list],
                [self.addBtn, self.removeBtn],
                ["Country", self.country],
                ["Region", self.region],
                ["City", self.city],
                ["Details", self.details]]
        
        [self.form.addRow(*row) for row in rows]
        
        self.setLayout(self.form)
        
        self._last = (-1, None)
    
    def updateList(self):
        en = (self.list.count() > 0)
        self.list.setEnabled(en)
        for i in [self.country, self.region, self.city, self.details]:
            i.setEnabled(en)
        
        index = self.list.currentIndex()
        self.removeBtn.setEnabled(index != -1)
    
    def save(self):
        if self._last[1] is not None:
            self._last[1].country = self.country.text()
            self._last[1].region = self.region.text()
            self._last[1].city = self.city.text()
            self._last[1].details = self.details.toPlainText()
    
    def onAddressChanged(self):
        self.save()
        
        index = self.list.currentIndex()
        tmp = self.list.itemData(index)
        self._last = (index, tmp)
        
        if self._last[1] is not None:
            self.country.setText(self._last[1].country)
            self.region.setText(self._last[1].region)
            self.city.setText(self._last[1].city)
            self.details.setText(self._last[1].details)
        else:
            self.country.setText("")
            self.region.setText("")
            self.city.setText("")
            self.details.setText("")
    
    def onAddButton(self):
        tmp = TempAddress()
        self.__tmp.append(tmp)
        self.list.addItem('New Address', tmp)
        
        self.updateList()
    
    def onRemoveButton(self):
        index = self.list.currentIndex()
        if index == -1:
            return
        tmp = self.list.itemData(index)
        tmp.removed = True
        self.list.removeItem(index)
        
        self.updateList()
    
    def setAddresses(self, addresses):
        self.__tmp = []
        self.list.clear()
        for a in addresses:
            tmp = TempAddress(a)
            self.__tmp.append(tmp)
            self.list.addItem('Address %d' % (a.id,), tmp)
        
        self.updateList()
    
    def addresses(self):
        self.save()
        return [tmp for tmp in self.__tmp if not tmp.removed]

class TempAddress(object):
    country = ''
    region = ''
    city = ''
    details = ''
    address = None
    removed = False
    def __init__(self, address=None):
        self.address = address
        if address is not None:
            self.country = address.country
            self.region = address.region
            self.city = address.city
            self.details = address.details
