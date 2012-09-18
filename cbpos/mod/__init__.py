import os
import cbpos

modules_path = [os.path.abspath(path) for path in cbpos.config['mod', 'modules_path'].split(':')]
__path__.extend(modules_path)