from setuptools import setup
import json


with open('metadata.json') as fp:
    metadata = json.load(fp)


setup(
    name='lexibank_suntb',
    description=metadata['title'],
    license=metadata.get('license', ''),
    url=metadata.get('url', ''),
    py_modules=['lexibank_suntb'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'lexibank.dataset': [
            'suntb=lexibank_suntb:Dataset',
        ]
    },
    install_requires=[
        'pylexibank>=2.0.0',
        'segments==2.0.2'
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)

