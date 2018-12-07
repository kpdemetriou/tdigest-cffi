from os import path
from setuptools import setup, find_packages

with open(path.join(path.abspath(path.dirname(__file__)), "README.rst"), encoding="utf-8") as handle:
    readme = handle.read()

setup(
    name="tdigest-cffi",
    version="0.1.2",
    description="A data structure for accurate on-line accumulation of rank-based statistics.",
    long_description=readme,
    url="https://github.com/kpdemetriou/tdigest-cffi",
    author="Phil Demetriou",
    author_email="inbox@philonas.net",
    license="BSD",
    packages=find_packages(exclude=["tests"]),
    setup_requires=["cffi>=1.4.0"],
    cffi_modules=["build.py:tdigest_ffi"],
    install_requires=["cffi>=1.4.0", "readerwriterlock==1.0.2"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: C",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Utilities",
    ],
)
