from setuptools import find_packages
from distutils.core import setup

if __name__== '__main__':
    setup(include_package_data=True,
          description='Scripts specific to gp15 water mass analysis on GP02 transect data',
          long_description="""Scripts specific to gp02 water mass analysis""",
          author="Rian Lawrence",
          author_email="rian@stanford.edu",
          url='https://github.com/nitrogenlab/gp15wmascripts&subdirectory=GP02wma@main',
          version='0.1.0.0',
          packages=find_packages(),
          setup_requires=[],
          install_requires=['gsw', 'pyompa'],
          scripts=[],
          name='gp02wma')
