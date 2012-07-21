import os, zipfile, shutil
import ConfigParser
import time

import app

def enableModule(mod_names, enable=True):
    disabled_str = app.config['mod', 'disabled_modules']
    disabled_set = set(disabled_str.split(',')) if disabled_str != '' else set()
    if type(mod_names) == str:
        mod_names = [mod_names]
    
    if enable:
        for mod_name in mod_names:
            disabled_set.discard(mod_name)
    elif enable is None:
        for mod_name in mod_names:
            if mod_name in disabled_set:
                disabled_set.discard(mod_name)
            else:
                disabled_set.add(mod_name)
    else:
        for mod_name in mod_names:
            disabled_set.add(mod_name)
    
    app.config['mod', 'disabled_modules'] = ','.join(disabled_set)
    app.config.save()

disableModule = lambda mod_name: enableModule(mod_name, enable=False)
toggleModule = lambda mod_name: enableModule(mod_name, enable=None)

def getInstallerInfo(target):
    z = zipfile.ZipFile(target, 'r')

    if 'install.cfg' not in z.namelist() or \
        [1 for name in z.namelist() if not name.startswith('app/modules/') and \
                                        not name.startswith('res/')].count(1)>1:
        return False
    
    config_file = z.open('install.cfg', 'r')
    config = ConfigParser.SafeConfigParser()
    config.readfp(config_file)
    
    base_name, name, version = config.get('info', 'base_name'), config.get('info', 'name'), config.get('info', 'version')
    z.close()
    return (base_name, name, version)

def installModule(target, info=None, replace=False):
    if info is None:
        info = getInstallerInfo(target)
        if not info:
            return False
    elif not info:
        return False
    
    installed = app.modules.isInstalled(info[0])
    if not replace and installed:
        return False
    elif replace and installed:
        base_name, name, version = installed
        uninstallModule(base_name, remove_resources=False)
    
    z = zipfile.ZipFile(target, 'r')
    
    members = z.namelist()
    members.remove('install.cfg')
    z.extractall(members=members)
    z.close()
    # TODO: add the module to the module list in app.modules as disabled

def uninstallModule(mod_name, remove_resources=True):
    enableModule(mod_name)
    shutil.rmtree('./app/modules/'+mod_name)
    if remove_resources:
        shutil.rmtree('./res/'+mod_name)
    # TODO: remove the module from the module list in app.modules
    return True

def exportModule(mod, target, export_source=False):
    z = zipfile.PyZipFile(target, 'w')

    config_filename = 'res/installer/modconfig/%s.cfg' % (mod.name,)
    config_file = open(config_filename, 'w')
    
    config = ConfigParser.SafeConfigParser()
    config.add_section('info')
    config.set('info', 'base_name', str(mod.name))
    config.set('info', 'name', str(mod.loader.name))
    config.set('info', 'version', str(mod.loader.version))
    
    config.write(config_file)
    config_file.close()
    
    z.write(config_filename, 'install.cfg')
    
    if export_source:
        os.path.walk('app/modules/'+mod.name, lambda *args: zipdirectory(*args, ignore_hidden=True), z)
    else:
        z.writepy('app/modules/'+mod.name, 'app/modules')
    os.path.walk('res/'+mod.name, zipdirectory, z)
    z.close()

def zipdirectory(z, dirname, filenames, ignore_hidden=True):
    if ignore_hidden:
        [filenames.remove(fname) for fname in filenames[:] if fname.startswith('.')] 
    if len(filenames) == 0:
        now = time.localtime(time.time())[:6]
        info = zipfile.ZipInfo(dirname+os.path.sep)
        info.date_time = now
        info.compress_type = zipfile.ZIP_STORED
        z.writestr(info, '')
    else:
        for fname in filenames:
            path = os.path.join(dirname, fname)
            if os.path.isdir(path): continue
            z.write(path, path)
