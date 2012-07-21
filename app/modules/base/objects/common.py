import app.database

#from sqlalchemy import func, Table, Column, Integer, String, Float, Boolean, Enum, DateTime, MetaData, ForeignKey
#from sqlalchemy.orm import relationship, backref

class Item:
    # TODO arrange soft deletions to have 3 tables (or more) one mother(id only), one active children, one deleted children
    #        see bookmark "The trouble with soft delete"
    #date_deleted = Column(DateTime, nullable=True, default=None)
    def fillDict(self, D):
        for k in D.keys():
            try:
                D[k] = getattr(self, k)
            except AttributeError:
                pass

    def update(self, **kwargs):
        session = app.database.session()
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        if not self in session:
            session.add(self)
        session.commit()
        return True

    def delete(self):
        session = app.database.session()
        session.delete(self)
        # TODO check the soft delete thingy
        #self.date_deleted = func.now()
        session.commit()
        return True
