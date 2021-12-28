Welcome to async-riot-api documentation!
========================================

async-riot-api is a Python library for `League of Legends`_ (and other `Riot Games`_' games) players
that offers an async and simple-to-use implementation of the `Riot Games APIs`_ based on `Asyncio`_.

Get started
^^^^^^^^^^^

.. hlist::
    :columns: 2

    - :doc:`Quick Start <start/quickstart>`: To get started quickly.
    - :doc:`API Access <start/auth>`: To get an API token.
    - :doc:`API Interaction <start/interaction>`: To interact with the API.

API reference
^^^^^^^^^^^^^

.. hlist::
    :columns: 2

    - :doc:`LoLAPI class <api/lolapi>`: Details about the main class for interacting with the API.
    - :doc:`Types <api/types>`: List of the implemented types.

.. toctree::
    :hidden:
    :caption: First of all

    start/auth
    start/interaction
    start/quickstart

.. toctree::
    :hidden:
    :caption: Methods and types

    api/lolapi
    api/types

.. toctree::

.. autosummary::
   :toctree: _autosummary
   :recursive:

   async_riot_api

.. _Riot Games: https://www.riotgames.com/
.. _League of Legends: https://www.leagueoflegends.com/
.. _Riot Games APIs: https://developer.riotgames.com/
.. _Asyncio: https://docs.python.org/3/library/asyncio.html