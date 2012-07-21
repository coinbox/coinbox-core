import app

import app.modules.base.objects.common as common

from sqlalchemy import func, Table, Column, Integer, String, Float, Boolean, MetaData, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, Comparator

permission_restriction_link = Table('permission_restriction', app.database.Base.metadata,
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
    Column('restriction_id', Integer, ForeignKey('menurestrictions.id'), primary_key=True)
)

class MenuRestriction(app.database.Base, common.Item):
    __tablename__ = "menurestrictions"
    __table_args__ = (
        UniqueConstraint('root', 'item'),
        )

    id = Column(Integer, primary_key=True)
    root = Column(String(255), nullable=False)
    item = Column(String(255), nullable=False)

    @hybrid_property
    def display(self):
        return self.root+'.'+self.item
    
    @display.expression
    def display(self):
        return func.concat(self.root, '.', self.item)

    def __repr__(self):
        return "<MenuRestriction %s.%s>" % (self.root, self.item)

class Permission(app.database.Base, common.Item):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=False)

    menu_restrictions = relationship("MenuRestriction", secondary=permission_restriction_link, backref="permissions")

    @hybrid_property
    def display(self):
        return self.name
    
    @display.expression
    def display(self):
        return self.name

    def __repr__(self):
        return "<Permission %s>" % (self.name,)
