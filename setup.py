import setuptools

setuptools.setup(
    name='genequery',
    license='GPL-3',
    version='0.1dev',
    author='Matthew Lazeroff',
    author_email='lazeroff@unlv.nevada.edu',
    description='Utilties for analyzing Fasta DNA Sequences with GeneMark/Glimmer',
    url='https://github.com/mlazeroff/GeneQuery',
    packages=['GeneQuery'],
    install_requires=['requests',
                      'beautifulsoup4',
                      'openpyxl'],
    classifiers=["Programming Language :: Python :: 3",
                 "License :: OSI Approved :: GPL-3",
                 "Operating System :: Windows"],
    scripts=['bin/gene_query.pyw'],
    include_package_data=True
)
