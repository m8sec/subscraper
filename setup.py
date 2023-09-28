from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='SubScraper',
    version='4.0.0',
    author='m8sec',
    description='Subdomain Enumeration Tool',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/m8r0wn/subscraper',
    license='GPLv3',
    packages=find_packages(include=[
        "subscraper", "subscraper.*"
    ]),
    package_data={
      'subscraper': ['data/*']
    },
    install_requires=[
        'censys>=2.2.6',
        'taser>=0.4.0',
        'ipparser>=1.0.0',
    ],
    classifiers= [
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Topic :: Security"
    ],
    entry_points={
        'console_scripts': ['subscraper=subscraper:main']
    }
)
