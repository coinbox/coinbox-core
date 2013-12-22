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
    
    def __repr__(self):
        return '<Driver %s>' % (self.name,)

class SQLiteDriver(Driver):
    name = 'sqlite'
    display = 'SQLite'
    form = {"database": {"label": "Filename", "required": False, "default": None}}

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

class MsSQLDriver(Driver):
    name = 'mssql'
    display = 'Microsoft SQL Server'
    form = {"host": {"label": "Host", "required": True, "default": ""},
            "port": {"label": "Port", "required": False, "default": 1433},
            "username": {"label": "Username", "required": False, "default": None},
            "password": {"label": "Password", "required": False, "default": None},
            "database": {"label": "Database", "required": True, "default": None}
            }

DRIVERS = {'sqlite': SQLiteDriver(), 'mysql': MySQLDriver(), 'postgresql': PostgreSQLDriver(),
           'firebird': FirebirdDriver(), 'mssql': MsSQLDriver()}

def get_driver(driver_name):
    return DRIVERS[driver_name.split("+", 1)[0]] 

def all_drivers():
    return DRIVERS.values()
