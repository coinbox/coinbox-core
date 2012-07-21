import app

import app.modules.base.objects.common as common

from sqlalchemy import func, Table, Column, Integer, String, Float, Boolean, Enum, DateTime, MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, Comparator

class CashFlow(app.database.Base, common.Item):
    __tablename__ = 'cashflow'

    id = Column(Integer, primary_key=True)
    source = Column(String(255), nullable=False)
    details = Column(String(255), nullable=False)
    date = Column(DateTime, default=func.current_timestamp())
    value = Column(Float, nullable=False)
    currency_id = Column(Integer, ForeignKey('currencies.id'))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    currency = relationship("Currency", backref="cashflow")
    user = relationship("User", backref="cashflow")
    
    @hybrid_property
    def display(self):
        return '#%d' % (self.id,)
    
    @display.expression
    def display(self):
        return func.concat('#', self.id)
    
    def __repr__(self):
        return "<CashFlow %s>" % (self.id,)
