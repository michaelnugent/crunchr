#!/usr/bin/env python3

from setuptools import setup
from sys import version_info


assert version_info >= (3, 8, 0), "crunchr.py requires >= Python 3.8"
INSTALL_REQUIRES = ["click", "jsonschema"]


setup(
    name="crunchr",
    version="1.0.0",
    description=("crunchr log processors"),
    long_description="crunchr log processor",
    packages=["crunchr"],
    author="Mike Nugent",
    author_email="michael@michaelnugent.org",
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.8",
    install_requires=INSTALL_REQUIRES,
    entry_points={"console_scripts": ["crunchr = crunchr.crunchr:cli"]},
)
