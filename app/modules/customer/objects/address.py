import app

import app.modules.base.objects.common as common

from sqlalchemy import func, Table, Column, Integer, String, Float, Boolean, Enum, MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, Comparator

class CustomerAddress(app.database.Base, common.Item):
    __tablename__ = 'customeraddresses'

    id = Column(Integer, primary_key=True)
    country = Column(String(255), nullable=False, default='')
    region = Column(String(255), nullable=False, default='')
    city = Column(String(255), nullable=False, default='')
    details = Column(String(255), nullable=False, default='')
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)

    customer = relationship("Customer", backref=backref("addresses", cascade="all, delete-orphan"))

    @hybrid_property
    def display(self):
        # TODO arrange the display property and expression of CustomerAddress, i think it should be unique
        return self.city+'/'+self.details
    
    @display.expression
    def display(self):
        return func.concat(self.city, '/', self.details)

    def __repr__(self):
        return "<CustomerAddress %s country=%s region=%s city=%s details=%s>" % (self.customer.name, self.country, self.region, self.city, self.details)
