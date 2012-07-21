import app

import app.database
import app.modules.base.objects.common as common

from sqlalchemy import func, Table, Column, Integer, String, Float, Boolean, MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, Comparator

class CustomerGroup(app.database.Base, common.Item):
    __tablename__ = 'customergroups'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    comment = Column(String(255), nullable=True)

    @hybrid_property
    def display(self):
        return self.name
    
    @display.expression
    def display(self):
        return self.name

    def __repr__(self):
        return "<CustomerGroup %s>" % (self.name)
