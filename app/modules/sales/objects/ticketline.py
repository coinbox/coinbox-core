import app

import app.modules.base.objects.common as common

from sqlalchemy import func, Table, Column, Integer, String, Float, Boolean, MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, Comparator

class TicketLine(app.database.Base, common.Item):
    __tablename__ = 'ticketlines'

    id = Column(Integer, primary_key=True)
    description = Column(String(255), nullable=False, default='')
    sell_price = Column(Float, nullable=False, default=0)
    amount = Column(Integer, nullable=False, default=1)
    discount = Column(Float, nullable=False, default=0)
    is_edited = Column(Boolean, nullable=False, default=False)
    ticket_id = Column(Integer, ForeignKey('tickets.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    
    ticket = relationship("Ticket", backref=backref("ticketlines", cascade="all, delete-orphan"))
    product = relationship("Product", backref="ticketlines")

    def update(self, **kwargs):
        p = self.product
        if not self.is_edited and p is not None:
            description_edited = ('description' in kwargs and self.description != kwargs['description'])
            price_edited = ('sell_price' in kwargs and self.sell_price != kwargs['sell_price'])
            kwargs.update({'is_edited': (description_edited or price_edited)})
        common.Item.update(self, **kwargs)

    @hybrid_property
    def display(self):
        return str(self.ticket.id)+'/'+str(self.id)
    
    @display.expression
    def display(self):
        return func.concat(self.ticket.id, '/', self.id)

    @hybrid_property
    def actual_price(self):
        return self.sell_price*(1.0-self.discount)
    
    @actual_price.expression
    def actual_price(self):
        return self.sell_price*(1.0-self.discount)

    @hybrid_property
    def total(self):
        return self.amount*self.sell_price*(1.0-self.discount)
    
    @total.expression
    def total(self):
        return self.amount*self.sell_price*(1.0-self.discount)

    def __repr__(self):
        return "<TicketLine %s in Ticket #%s>" % (self.id, self.ticket.id)
