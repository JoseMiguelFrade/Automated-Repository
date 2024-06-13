from setuptools import setup, find_packages

setup(
    name='my_project',
    version='0.1',
    packages=find_packages(where='backend'),
    install_requires=[
        'beautifulsoup4',
        'click',
        'requests',
        'selenium',
        'requests_html',
        'psutil',
        'flask',
        'flask-cors',
        'flask-socketio',
        'pymongo',
    ],
    extras_require={
        'tests': [
            'pytest',
            'pytest-cov',
            'pytest-flakes',
            'pytest-pep8',
        ],
    },
)
