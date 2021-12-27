LoLAPI Client
===============

You have entered the API Reference section where you can find detailed information about Pyrogram's API. The main Client
class, all available methods and types, filters, handlers, decorators and bound-methods detailed descriptions can be
found starting from this page.

This page is about the Client class, which exposes high-level methods for an easy access to the API.

.. code-block:: python

    from async_riot_api import LoLAPI

    async def main():
        api = LoLAPI('my_token')

        me = await api.get_summoner_by_name('my summoner name')
        print(me)

    asyncio.get_event_loop().run_until_complete(main())



-----

Details
-------

.. autoclass:: async_riot_api.LoLAPI()
