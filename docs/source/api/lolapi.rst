LoLAPI class
=============

On this page you will find the list of methods available for the :doc:`LoLAPI <../api/lolapi>` class.
Dispite the name, :doc:`LoLAPI <../api/lolapi>` is not only for League of Legends, but includes all the methods from the original Riot Games API.

The majority of methods in this class are a direct implementation of Riot Games API methods, while the others are extras made to add features and (hopefully) simplify your experience with this library.
Those that return the result of an API method always return an instance of a subclass of :class:`~async_riot_api.types.RiotApiResponse`.

.. autoclass:: async_riot_api.LoLAPI()
    :members:
    :member-order: bysource
    :automodule_typehints: none
