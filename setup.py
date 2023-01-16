#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build python package
"""

from os.path import dirname, join, abspath
from setuptools import setup, find_packages
# def read_requirements(file):
#    with open(file) as f:
#        return f.read().splitlines()


def read(rel_path: str) -> str:
    """
    Get content of file
    """
    here = abspath(dirname(__file__))
    with open(join(here, rel_path), encoding="utf-8") as file:
        return file.read()


def get_version(rel_path: str) -> str:
    """
    Get version of python module
    """
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


# requirements = read_requirements("requirements.txt")

def main() -> None:
    """
    run setup
    """
    setup(
        name="easyunicornpkg",
        version=get_version("easyunicornpkg/__init__.py"),
        author="Commandcracker",
        project_urls={
            "Source": "https://github.com/unicornpkg/easyunicornpkg",
            "Tracker": "https://github.com/unicornpkg/easyunicornpkg/issues"
        },

        description="Python utility to build a unicornpkg package table.",
        long_description_content_type="text/markdown",
        long_description=read("README.md"),

        py_modules=["easyunicornpkg"],

        license="Apache Software License",
        packages=find_packages(exclude=["test"]),
        # install_requires=requirements,
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",

            "License :: OSI Approved :: Apache Software License",

            "Operating System :: OS Independent",

            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",
        ],
        entry_points={
            'console_scripts': ['easyunicornpkg=easyunicornpkg.easyunicornpkg:main'],
        }
    )


if __name__ == "__main__":
    main()
