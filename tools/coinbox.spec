# -*- mode: python -*-

import glob, os

cwd = os.getcwd()

a = Analysis(['coinbox.py'],
             pathex=[cwd],
             hiddenimports=['cbpos'],
             hookspath=[os.path.join('tools', 'hooks')])

import cbpos

for mp in set(os.path.normcase(os.path.realpath(p)) for p in cbpos.mod.__path__):
    p = len(mp)
    for res in glob.glob(os.path.join(mp, '*', 'res')):
        for root, dirnames, filenames in os.walk(res):
            relroot = root[p:].strip(os.path.sep)
            for f in filenames:
                a.datas.append((os.path.join('cbpos', 'mod', relroot, f),
                                os.path.join(root, f),
                                'DATA'))

a.datas.append(('coinbox.ico', os.path.join(cwd, 'coinbox.ico'), 'DATA'))
a.datas.append(('COPYING', os.path.join(cwd, 'COPYING'), 'DATA'))
a.datas.append(('README', os.path.join(cwd, 'README'), 'DATA'))

pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build', 'pyi.win32', 'coinbox', 'coinbox.exe'),
          debug=True,
          strip=None,
          upx=True,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'coinbox'))
