Interacting with the API
========================

All the interaction with the API is made using the :doc:`LoLAPI <../api/lolapi>` class.
    - First you create an object of type :doc:`LoLAPI <../api/lolapi>`.
    - Then you can start calling its methods, corresponding to api methods (or extra features like champion search)

Methods are async, meaning that you need to be in an async context to be able to use this library. Async methods mean that you can use
the features offered by `asyncio <https://docs.python.org/3/library/asyncio.html>`_ to enhance your performances.

For example, imagine you want to get rank information about the ten participants of a match.
Without using asyncio features you would do something like this:

.. code-block:: python

    ranks = [await api.get_solo_league(p.summonerId) for p in match.participants]

This would take a relatively long time to finish, about more than 1.5s.

Now, let's use the function ``gather`` from asyncio:

.. code-block:: python

    ranks = await asyncio.gather(
        *[api.get_solo_league(p.summonerId) for p in match.participants]
    )

This time the code would execute in far less time than before, thanks to ``asyncio.gather`` running all the coroutines in a parallel way.
This way the time required to finish this call is the maximum time required by a single request, and not the sum of all requests.