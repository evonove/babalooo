from setuptools import setup

setup(
    name = 'babalooo',
    version = '0.1',
    py_modules = ['ebay'],
    install_requires = [
        'Click',
    ],
    entry_points = '''
        [console_scripts]
        babalooo = ebay:main
        ''',
)
