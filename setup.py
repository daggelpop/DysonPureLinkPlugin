from distutils.core import setup

setup(
    name='DysonPureLinkPlugin',
    version='0.1',
    packages=['DysonPureLinkPlugin'],
    url='https://github.com/UBayouski/DysonPureLinkPlugin',
    license='MIT',
    author='UBayouski',
    author_email='',
    description='',
    install_requires=[
        'paho-mqtt',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'dyson_run_plugin = DysonPureLinkPlugin.run_plugin:main'
        ]
    },
)
