__all__ = ('Driver', 'DriverNotFoundError')

class Driver(object):
    name = None
    display = 'Generic Driver'
    form = {"host": {"label": "Host", "required": False, "default": None},
            "port": {"label": "Port", "required": False, "default": None},
            "username": {"label": "Username", "required": False, "default": None},
            "password": {"label": "Password", "required": False, "default": None},
            "database": {"label": "Database", "required": False, "default": None},
            "query": {"label": "Query", "required": False, "default": None}
            }
    empty_fields = frozenset()
    use_database_as_filename = False
    
    def __repr__(self):
        return '<Driver %s>' % (self.name,)
    
    __drivers = {}
    @classmethod
    def get(cls, driver_name):
        return cls.__drivers[driver_name.split("+", 1)[0]]
    
    @classmethod
    def get_all(cls):
        return cls.__drivers.values()
    
    @classmethod
    def register(cls, driver_cls):
        cls.__drivers[driver_cls.name] = driver_cls

class SQLiteDriver(Driver):
    name = 'sqlite'
    display = 'SQLite'
    form = {"database": {"label": "Filename", "required": False, "default": None}}
    empty_fields = frozenset(("host", "port", "username", "password"))
    use_database_as_filename = True

class MySQLDriver(Driver):
    name = 'mysql'
    display = 'MySQL'
    form = {"host": {"label": "Host", "required": True, "default": ""},
            "port": {"label": "Port", "required": False, "default": 3306},
            "username": {"label": "Username", "required": False, "default": None},
            "password": {"label": "Password", "required": False, "default": None},
            "database": {"label": "Database", "required": True, "default": ""}
            }

class PostgreSQLDriver(Driver):
    name = 'postgresql'
    display = 'PostgreSQL'
    form = {"host": {"label": "Host", "required": True, "default": ""},
            "port": {"label": "Port", "required": False, "default": 5432},
            "username": {"label": "Username", "required": False, "default": None},
            "password": {"label": "Password", "required": False, "default": None},
            "database": {"label": "Database", "required": True, "default": ""}
            }

class FirebirdDriver(Driver):
    name = 'firebird'
    display = 'Firebird'
    form = {"host": {"label": "Host", "required": False, "default": ""},
            "port": {"label": "Port", "required": False, "default": 3050},
            "username": {"label": "User", "required": False, "default": None},
            "password": {"label": "Password", "required": False, "default": None},
            "database": {"label": "Filename", "required": True, "default": ""}
            }
    use_database_as_filename = True

class MsSQLDriver(Driver):
    name = 'mssql'
    display = 'Microsoft SQL Server'
    form = {"host": {"label": "Host", "required": True, "default": ""},
            "port": {"label": "Port", "required": False, "default": 1433},
            "username": {"label": "Username", "required": False, "default": None},
            "password": {"label": "Password", "required": False, "default": None},
            "database": {"label": "Database", "required": True, "default": None}
            }

Driver.register(SQLiteDriver)
Driver.register(MySQLDriver)
Driver.register(PostgreSQLDriver)
Driver.register(FirebirdDriver)
Driver.register(MsSQLDriver)

class DriverNotFoundError(ValueError):
    pass
