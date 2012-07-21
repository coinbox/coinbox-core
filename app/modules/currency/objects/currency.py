import app

import app.modules.base.objects.common as common

from sqlalchemy import func, Table, Column, Integer, String, Float, Boolean, MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, Comparator

class Currency(app.database.Base, common.Item):
    __tablename__ = 'currencies'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    symbol = Column(String(5), nullable=False, unique=True)
    value = Column(Float, nullable=False)
    decimal_places = Column(Integer, nullable=False, default=2)
    digit_grouping = Column(Boolean, default=False)

    @hybrid_property
    def display(self):
        return self.name
    
    @display.expression
    def display(self):
        return self.name

    def __repr__(self):
        return "<Currency %s>" % (self.symbol,)

    def getFormatString(self):
        return (',' if self.digit_grouping else '')+\
               ('.%df' % (max(0, self.decimal_places),))

    def format(self, value):
        return '%s %s' % (format(round(value, max(0, self.decimal_places)), self.getFormatString()), self.symbol)

default = None
def get_default():
    global default
    currency_id = app.config['mod.currency', 'default']
    currency_id = None if currency_id == '' else currency_id
    if default is not None and currency_id == default[0]:
        return default[1]
    session = app.database.session()
    if currency_id is not None:
        default = (currency_id, session.query(Currency).filter_by(id=currency_id).one())
        return default[1]
    else:
        default = (None, session.query(Currency).first())
        return default[1]

def convert(price, src_currency, dest_currency):
    s_val = float(src_currency.value)
    d_val = float(dest_currency.value)
    #ps*vs = pd*vd

    return float(price)*s_val/d_val
    #return round(float(price)*s_val/d_val, dest_currency.decimal_places)
