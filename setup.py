from setuptools import setup, find_packages

setup(
    name="python-emec-api",
    version="0.0.2",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.9.1",
        "beautifulsoup4>=4.12.2",
    ],
    author="natanrmaia",
    author_email="contato@natanael.dev.br",
    description="Python module created to integrate your Python project with the EMEC API",
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/natanrmaia/python-emec-api",
    project_urls={
        'Documentation': 'https://python-emec-api.readthedocs.io/en/latest/',
        'Source': 'https://github.com/natanrmaia/python-emec-api',
        'Bug Reports': 'https://github.com/natanrmaia/python-emec-api/issues',
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
