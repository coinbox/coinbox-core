from setuptools import setup, find_packages

# Custom commands to build using PyInstaller and NSIS
from setuptools import Command
from distutils.errors import DistutilsOptionError, DistutilsSetupError
import os
import subprocess

class PyInstallerCommand(Command):
    """
    Command which runs the PyInstaller spec file for Coinbox
    with the appropriate parameters.
    Requires PyInstaller to be installed in Python's path.
    """
    description = 'run PyInstaller script'
    user_options = []
    boolean_options = []

    def initialize_options(self):
        self.pyi_run = None

    def finalize_options(self):
        try:
            from PyInstaller.main import run
        except ImportError:
            raise DistutilsOptionError('PyInstaller is not installed')
        else:
            self.pyi_run = run

    def run(self):
        spec_file = os.path.join(os.path.dirname(__file__), "tools", "coinbox.spec")
        
        self.pyi_run([spec_file])

class NSISCommand(Command):
    """
    Command which runs the NSIS installer for Coinbox
    with the appropriate parameters.
    Requires NSIS to be installed and its install directory be known.
    """
    description = 'run NSIS installer script'
    user_options = [
        ('nsis-dir=', 'n',
         "installation directory of NSIS"),
    ]
    boolean_options = []

    def initialize_options(self):
        self.nsis_dir = None
        self.nsis_exec = None

    def finalize_options(self):
        if self.nsis_dir is None:
            pathlist = os.environ.get('PATH', os.defpath).split(os.pathsep)
            programfiles = os.environ.get('PROGRAMFILES',
                os.path.join("C:", "Program Files"))
            programfilesx86 = os.environ.get('PROGRAMFILES(X86)',
                os.path.join("C:", "Program Files (x86)"))
            pathlist.extend([
                ".",
                os.path.join(programfiles, "NSIS"),
                os.path.join(programfilesx86, "NSIS")
                ])
        else:
            pathlist = [self.nsis_dir]
        
        filenames = ('makensis', 'makensis.exe')
        
        self.nsis_exec = self.__find_nsis_exec(pathlist, filenames)
        
        if self.nsis_exec is None:
            raise DistutilsOptionError(
                "Error: makensis executable not found, "
                "add NSIS directory to the path or specify it "
                "with --nsis-dir")

    def __find_nsis_exec(self, pathlist, filenames):
        for path in pathlist:
            for fname in filenames:
                makensis = os.path.join(path, fname)
                if os.path.isfile(makensis):
                    return makensis

    def run(self):
        nsi_file = os.path.join(os.path.dirname(__file__), "tools", "installer.nsi")
        
        subprocess.call([self.nsis_exec, "-NOCD", "--", nsi_file])

setup(
      name="Coinbox-pos",
      version="0.2",
      packages=find_packages(),
      scripts=['coinbox'],
      
      zip_safe=True,
      
      namespace_packages=['cbmod'],
      include_package_data=True,
      
      install_requires=[
			'sqlalchemy>=0.7, <1.0',
			'PyDispatcher>=2.0.3, <3.0',
			'ProxyTypes>=0.9, <1.0',
			'Babel>=1.3, <2.0'
      ],
      
      cmdclass={'bdist_pyi': PyInstallerCommand,
                'bdist_nsis': NSISCommand},
      
      author='Coinbox POS Team',
      author_email='coinboxpos@googlegroups.com',
      description='Coinbox POS core package',
      license='MIT',
      url='http://coinboxpos.org/'
)
