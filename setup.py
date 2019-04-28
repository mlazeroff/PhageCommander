import setuptools

setuptools.setup(
    name='genequery',
    license='GPL-3',
    version='0.1dev',
    author='Matthew Lazeroff',
    author_email='lazeroff@unlv.nevada.edu',
    description='Utilties for analyzing Fasta DNA Sequences with GeneMark/Glimmer',
    url='https://github.com/mlazeroff/GeneQuery',
    packages=['genequery'],
    package_data={'genequery': ['species.txt', 'prodigal.windows.exe']},
    install_requires=['requests',
                      'beautifulsoup4',
                      'openpyxl'],
    entry_points={'console_scripts': 'gquery = genequery.gquery:main',
                  'gui_scripts': 'genequery = genequery.gene_query:main'},
    classifiers=["Programming Language :: Python :: 3",
                 "License :: OSI Approved :: GPL-3",
                 "Operating System :: Windows"],
    include_package_data=True
)
