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
    install_requires=['requests',
                      'beautifulsoup4',
                      'openpyxl'],
    classifiers=["Programming Language :: Python :: 3",
                 "License :: OSI Approved :: GPL-3",
                 "Operating System :: Windows"],
    entry_points={
        'gui_scripts': ['GeneQuery=genequery.gene_query:main']
    },
    include_package_data=True
)
