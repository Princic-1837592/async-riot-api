Installation Guide
==================

The library's code itself does not require a specific python version (except for Python 3) since it's simple Python code.
The only requirements are for your Python version to support the required libraries, especially `Asyncio`_ and `aiohttp`_.

.. contents:: Contents
    :backlinks: none
    :depth: 1
    :local:

-----

Install async-riot-api
----------------------

Use the classical pip method to install the library
.. code-block:: text
    $ pip3 install -U async-riot-api

Verifying
---------

To verify that async-riot-api is correctly installed, open a Python shell and import the library.
No error should show up.

.. parsed-literal::

    >>> import async_riot_api
    >>> async_riot_api.__version__
    'x.y.z'

.. _Asyncio: https://docs.python.org/3/library/asyncio.html
.. _aiohttp: https://docs.aiohttp.org/en/stable/