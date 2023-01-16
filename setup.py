from setuptools import setup, find_packages
from os.path import dirname, join, abspath
# def read_requirements(file):
#    with open(file) as f:
#        return f.read().splitlines()


def read(rel_path: str) -> str:
    here = abspath(dirname(__file__))
    with open(join(here, rel_path)) as fp:
        return fp.read()


def get_version(rel_path: str) -> str:
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


# requirements = read_requirements("requirements.txt")

def main() -> None:
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
