# -*- mode: python -*-

import glob, os

cwd = os.path.realpath(os.path.join(SPECPATH, '..')) #os.getcwd()

import cbmod

a = Analysis([os.path.join(cwd, 'coinbox.py')],
             hookspath=[os.path.join(cwd, 'tools', 'hooks')]
             )

for mp in set(os.path.normcase(os.path.realpath(p)) for p in cbmod.__path__):
    p = len(mp)
    for res in glob.glob(os.path.join(mp, '*', 'res')):
        for root, dirnames, filenames in os.walk(res):
            relroot = root[p:].strip(os.path.sep)
            for f in filenames:
                a.datas.append((os.path.join('cbmod', relroot, f),
                                os.path.join(root, f),
                                'DATA'))

# Used for the NSIS installer
a.datas.append(('coinbox.ico', os.path.join(cwd, 'coinbox.ico'), 'DATA')) # NSIS will need a full path to a .ico file
a.datas.append(('LICENSE', os.path.join(cwd, 'LICENSE'), 'DATA'))
a.datas.append(('README', os.path.join(cwd, 'README'), 'DATA'))

pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name='coinbox.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          icon=os.path.join(cwd, 'coinbox.ico'))

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join(cwd, 'dist', 'coinbox'))
