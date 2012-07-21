import app

import app.modules.base.objects.common as common

from sqlalchemy import func, Table, Column, Integer, String, Float, Boolean, MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, Comparator

role_permission_link = Table('role_permission', app.database.Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

class Role(app.database.Base, common.Item):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)

    permissions = relationship("Permission", secondary=role_permission_link, backref="roles")

    def isPermitted(self, permission):
        if permission is None:
            return True
        elif type(permission) == str:
            return (permission in [p.name for p in self.permissions])
        else:
            return (permission in self.permissions)

    @hybrid_property
    def display(self):
        return self.name
    
    @display.expression
    def display(self):
        return self.name

    def __repr__(self):
        return "<Role %s>" % (self.name,)
