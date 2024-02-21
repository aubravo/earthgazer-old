========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |github-actions|
        | |codecov|
        | |codacy|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/earthgazer/badge/?style=flat
    :target: https://earthgazer.readthedocs.io/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/aubravo/earthgazer/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/aubravo/earthgazer/actions

.. |codecov| image:: https://codecov.io/github/aubravo/earthgazer/graph/badge.svg?token=N96UW9UMJ8
    :alt: Coverage Status
    :target: https://app.codecov.io/github/aubravo/earthgazer

.. |codacy| image:: https://img.shields.io/codacy/grade/d7fd22bea5cf472f8acd1b359b416603.svg
    :target: https://app.codacy.com/gh/aubravo/earthgazer
    :alt: Codacy Code Quality Status


.. |version| image:: https://img.shields.io/pypi/v/earthgazer.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/earthgazer

.. |wheel| image:: https://img.shields.io/pypi/wheel/earthgazer.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/earthgazer

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/earthgazer.svg
    :alt: Supported versions
    :target: https://pypi.org/project/earthgazer

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/earthgazer.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/earthgazer

.. |commits-since| image:: https://img.shields.io/github/commits-since/aubravo/earthgazer/v1.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/aubravo/earthgazer/compare/v1.0.0...main



.. end-badges

Satellite image processing pipeline

* Free software: GNU GENERAL PUBLIC LICENSE v3 or later (GPLv3+)

Installation
============

::

    pip install earthgazer

You can also install the in-development version with::

    pip install https://github.com/aubravo/earthgazer/archive/main.zip


Documentation
=============


https://earthgazer.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
