Quickstart with this library
============================

This is a very intuitive and simple to use library. Follow these steps to get started:
    - Get your API token following `this guide <start/auth>`_
    - Install the library in your (virtual) environment
    - Open your favourite text editor and paste the following code:

    .. code-block:: python
        from async_riot_api import LoLAPI
        import asyncio

        async def main():
            api = LoLAPI('token', 'region', 'routing value', True)
            me = await api.get_summoner('my summoner name')
            print(me.to_string())

        asyncio.get_event_loop().run_until_complete(main())

    - Replace values that need to be replaced