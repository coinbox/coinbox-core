import app

import app.modules.base.objects.common as common

from sqlalchemy import func, Table, Column, Integer, String, Float, Boolean, Enum, DateTime, MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, Comparator

class DiaryEntry(app.database.Base, common.Item):
    __tablename__ = 'stockdiary'

    id = Column(Integer, primary_key=True)
    operation = Column(Enum('in', 'out', 'edit'), nullable=False)
    quantity = Column(Integer, nullable=True)
    date = Column(DateTime, nullable=False, default=func.current_timestamp())
    product_id = Column(Integer, ForeignKey('products.id'))
    
    product = relationship("Product", backref="diaryentries")

    keys = ('operation', 'quantity', 'date', 'product')

    def __init__(self, *args, **kwargs):
        # Entry Date cannot be changed
        if 'date' in kwargs:
            del kwargs['date']
        app.database.Base.__init__(self, *args, **kwargs)

    @hybrid_property
    def display(self):
        # TODO arrange the display function, is it unique?
        return str(self.quantity)+self.operation+'/'+self.product.name
    
    @display.expression
    def display(self):
        return func.concat(self.quantity, self.operation, '/', self.product.name)

    def __repr__(self):
        return "<DiaryEntry %d %s of %s on %s>" % \
               (self.quantity, self.operation, self.product, self.date)
