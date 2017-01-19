from setuptools import setup

setup(
    name='arrflan',
    packages=['arrflan'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_sqlalchemy',
        'flask_openid'
    ],
)
