import os
import re

from setuptools import find_packages, setup

_version_re = re.compile(r"__version__\s+=\s+(.*)")


def read_version():
    regexp = re.compile(r'^__version__\W*=\W*"([\d.abrc]+)"')
    init_py = os.path.join(os.path.dirname(__file__), "smallder", "__init__.py")
    with open(init_py) as f:
        for line in f:
            match = regexp.match(line)
            if match is not None:
                return match.group(1)


def read(file_name):
    with open(
            os.path.join(os.path.dirname(__file__), file_name), mode="r", encoding="utf-8"
    ) as f:
        return f.read()


requires = [
    'annotated-types>=0.6.0',
    'anyio>=4.3.0',
    'async-timeout>=4.0.3',
    'certifi>=2024.2.2',
    'chardet>=5.2.0',
    'charset-normalizer>=3.3.2',
    'click>=8.1.7',
    'colorama>=0.4.6',
    'exceptiongroup>=1.2.0',
    'fastapi>=0.109.2',
    'greenlet>=3.0.3',
    'h11>=0.14.0',
    'idna>=3.6',
    'loguru>=0.7.2',
    'pydantic>=2.6.1',
    'pydantic_core>=2.16.2',
    'PyDispatcher>=2.0.7',
    'redis>=5.0.1',
    'requests>=2.30.0',
    'six>=1.16.0',
    'sniffio>=1.3.0',
    'SQLAlchemy>=2.0.29',
    'starlette>=0.36.3',
    'typing_extensions>=4.9.0',
    'urllib3>=1.25.10',
    'uvicorn>=0.27.1',
    'w3lib>=2.1.2',
    'PyMySQL>=1.1.0'
]

setup(
    name="smallder",
    version=read_version(),
    author="NTrash",
    author_email='yinghui0214@163.com',
    description="An out-of-the-box lightweight asynchronous crawler framework",
    python_requires=">=3.7",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    license="MIT",
    install_requires=requires,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
    ],
    entry_points={"console_scripts": ["smallder = smallder.commands.cmdline:execute"]},
)
