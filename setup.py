import re
from pathlib import Path

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    with Path(__file__).parent.joinpath(*names).open(encoding=kwargs.get("encoding", "utf8")) as fh:
        return fh.read()


setup(
    name="earthgazer",
    version="1.0.0",
    license="GPL-3.0-or-later",
    description="Satellite image processing pipeline",
    long_description="{}\n{}".format(
        re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub("", read("README.rst")),
        re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
    ),
    author="Alvaro Bravo",
    author_email="alvaroubravo@gmail.com",
    url="https://github.com/aubravo/earthgazer",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[path.stem for path in Path("src").glob("*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)" "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": "https://earthgazer.readthedocs.io/",
        "Changelog": "https://earthgazer.readthedocs.io/en/latest/changelog.html",
        "Issue Tracker": "https://github.com/aubravo/earthgazer/issues",
    },
    keywords=[
        # eg: "keyword1", "keyword2", "keyword3",
    ],
    python_requires=">=3.11",
    install_requires=[
        "click",
        "google-cloud-bigquery",
        "google-cloud-storage",
        "pydantic",
        "redis-om",
        "jinja2",
        "sqlalchemy",
        "rasterio",
        "numpy",
        "matplotlib",
        "pillow",
        "pydantic-settings",
        "fsspec",
        "gcsfs",
        "click_aliases",
    ],
    extras_require={
        # eg:
        #   "rst": ["docutils>=0.11"],
        #   ":python_version=="2.6"": ["argparse"],
    },
    entry_points={},
)
