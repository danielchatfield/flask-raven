from setuptools import setup

setup(
    name='flask_raven',
    version='0.0.4',
    install_requires=["flask", "pycrypto"],
    url='http://github.com/danielchatfield/flask-raven/',
    license='Artistic 2.0',
    author='Daniel Chatfield',
    author_email='chatfielddaniel@gmail.com',
    description='A flask extension for the University of Cambridge\'s '
                'authentication system',
    packages=['flask_raven'],
    platforms='any'
)
