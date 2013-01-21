from setuptools import setup, find_packages

setup(
      name="Coinbox POS",
      version="0.1",
      packages=find_packages()+['argparse'],
      scripts=['coinbox.py'],
      
      zip_safe=True,
      
      namespace_packages=['cbpos', 'cbpos.mod'],
      include_package_data=True,
      
      install_requires=['sqlalchemy>=0.7'],
      
      author='Coinbox POS Team',
      author_email='coinboxpos@googlegroups.com',
      description='Coinbox POS core package',
      license='GPLv3',
      url='http://coinboxpos.org/'
)
