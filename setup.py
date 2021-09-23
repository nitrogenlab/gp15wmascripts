from setuptools import find_packages
from distutils.core import setup

if __name__== '__main__':
    setup(include_package_data=True,
          description='Scripts specific to gp15 water mass analysis',
          long_description="""Scripts specific to gp15 water mass analysis""",
          author="Avanti Shrikumar",
          author_email="avanti.shrikumar@gmail.com",
          url='https://github.com/nitrogenlab/gp15wmascripts',
          version='0.1.0.0',
          packages=find_packages(),
          setup_requires=[],
          install_requires=['gsw', 'pyompa'],
          scripts=[],
          name='gp15wmascripts')
