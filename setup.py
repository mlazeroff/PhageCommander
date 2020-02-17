import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
    name='phage-commander',
    license='GPL-3',
    version='0.4.3dev',
    author='Matthew Lazeroff',
    author_email='lazeroff@unlv.nevada.edu',
    description='A graphical tool for predicting genes on phage DNA sequences',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mlazeroff/PhageCommander',
    packages=['phagecommander'],
    package_data={'phagecommander': ['species.txt', 'GuiWidgets/*', 'Utilities/*']},
    install_requires=['requests>=2.22.0',
                      'bs4>=4.8.2',
                      'openpyxl>=3.0.3',
                      'pyqt5>=5.14.1',
                      'biopython>=1.76',
                      'ruamel.yaml>=0.16.10'],
    entry_points={'gui_scripts': 'phagecom = phagecommander.phagecom:main'},
    classifiers=["Programming Language :: Python :: 3",
                 "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                 "Operating System :: Microsoft :: Windows",
                 "Operating System :: MacOS",
                 "Operating System :: Unix"],
    include_package_data=True,
)
