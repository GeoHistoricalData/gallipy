import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='gallipy',
    version='1.0.0',
    author="Bertrand Dumenieu",
    author_email="bertranddumenieu@gmail.com",
    description="A python tool to query the French National Library portal gallica.bnf.fr",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=[
        'xmltodict',
        'beautifulsoup4',
        'rfc3987',
        'lark-parser',
        'lxml',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
