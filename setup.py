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
    "chardet>=4.0.0",
    "loguru>=0.5.3",
    "lxml>=4.6.3",
    "PyDispatcher>=2.0.5",
    "pytest>=6.2.5",
    "redis>=3.5.3",
    "requests>=2.26.0",
    "setuptools>=56.0.0",
    "six>=1.16.0",
    "SQLAlchemy>=1.4.25",
    "starlette>=0.14.2",
    "urllib3>=1.26.6",
    "uvicorn>=0.15.0",
    "w3lib>=1.22.0",
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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["smallder = smallder.commands.cmdline:execute"]},
)
