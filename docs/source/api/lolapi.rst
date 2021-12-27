LoLAPI Client
===============

On this page you will find the list of methods available for the LoLAPI class.
The mahority of methods are a direct implementation of Riot Games' API methods, others are extras made to simplify your life.
Those that return the result of an API method always return an instance of a subclass of `types.RiotApiResponse`

It is important to notice that this implementation is exception-free, not meaning that it's impossible to make mistake,
but meaning that errors returned by the API are not raised as exceptions. Instead, they are returned as `types.RiotApiError`,
containing information about the error.
To distinguish between a successful response and an error, you can easily use the object as a boolean expression:
.. code-block:: python
    summoner = await api.get_account_by_puuid(puuid)
    if not summoner:
        print(f'The request raised an error with status code {summoner.status_code}: {summoner.message}')
    else:
        print(summoner.to_string(sep = '|   '))

.. autoclass:: async_riot_api.LoLAPI()
    :members:
