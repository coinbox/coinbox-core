import app

import app.modules.base.objects.common as common

from sqlalchemy import func, Table, Column, Integer, String, Float, Boolean, MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, Comparator

class Category(app.database.Base, common.Item):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey('categories.id'))

    parent = relationship("Category", backref="children", remote_side=[id])

    @hybrid_property
    def display(self):
        return self.name
    
    @display.expression
    def display(self):
        return self.name

    def __repr__(self):
        return "<Category %s>" % (self.name,)
