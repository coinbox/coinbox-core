import app

import app.modules.base.objects.common as common

from sqlalchemy import func, Table, Column, Integer, String, Float, Boolean, Enum, MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, Comparator

class CustomerContact(app.database.Base, common.Item):
    __tablename__ = 'customercontacts'

    id = Column(Integer, primary_key=True)
    name = Column(Enum('email', 'phone', 'mobile', 'fax'), nullable=False)
    value = Column(String(255), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)

    customer = relationship("Customer", backref=backref("contacts", cascade="all, delete-orphan"))

    @hybrid_property
    def display(self):
        # TODO arrange the display property and expression of CustomerContact, i think it should be unique
        return self.name+':'+self.value
    
    @display.expression
    def display(self):
        return func.concat(self.name, ':', self.value)

    def __repr__(self):
        return "<CustomerContact %s %s=%s>" % (self.customer.name, self.name, self.value)
