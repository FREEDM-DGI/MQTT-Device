from setuptools import setup

setup(name='freedmqtt',
      version='1.0',
      description='FREEDM MQTT Local Area Network Backend',
      url='',
      author='GEH Software Team',
      author_email='skumar15@ncsu.edu',
      license='NCSU',
      packages=['freedmqtt'],
      install_requires=[
      		'paho-mqtt',
      		'jsonpickle',
      		'xlrd',
      		'portalocker',
      		'nose',
      	],
      test_suit = 'nose.collector',
      tests_require = ['nose'],
      zip_safe=False)	