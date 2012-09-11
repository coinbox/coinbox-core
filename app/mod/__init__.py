import os
import app

modules_path = [os.path.abspath(path) for path in app.config['mod', 'modules_path'].split(':')]
__path__.extend(modules_path)