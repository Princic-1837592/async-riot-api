from typing import Any, Dict, List, Optional, Set, Tuple, Union
from json import loads
from fuzzywuzzy import fuzz
from aiohttp import ClientResponse, request
import asyncio
from urllib.parse import quote_plus
from pprint import pprint
import requests
from . import types


class LoLAPI:
    """
    https://developer.riotgames.com/apis
    """
    
    __BASE_URL: str = 'https://{}.api.riotgames.com{}'
    __VERSION: int = loads(requests.get('https://ddragon.leagueoflegends.com/api/versions.json').text)[0]
    __QUEUES: Dict[int, str] = {
        queue['queueId']: queue['description'].replace('games', '').strip() if queue['description'] else 'Custom'
        for queue in loads(requests.get('https://static.developer.riotgames.com/docs/lol/queues.json').text)
    }
    
    # correct champion name -> short champion
    __CHAMPS: Dict[str, Dict[str, Any]] = loads(
        requests.get(f'https://ddragon.leagueoflegends.com/cdn/{__VERSION}/data/en_US/champion.json').text
    )['data']
    
    # integer champion ID -> correct champion name
    __CHAMP_ID_TO_CORRECT_NAME: Dict[int, str] = {
        int(info['key']): champ for champ, info in __CHAMPS.items()
    }
    __LANGUAGES: List[str] = loads(requests.get('https://ddragon.leagueoflegends.com/cdn/languages.json').text)
    __LANG_SHORT_TO_LONG: Dict[str, str] = {
        'it': 'it_IT',
        'en': 'en_US'
    }
    
    def __init__(self, api_key: str, region: str = 'euw1', routing_value_v5: str = 'europe', debug: bool = False):
        self.api_key = api_key
        self.region = region
        self.v5_routing_value = routing_value_v5
        self.debug = debug
    
    @staticmethod
    async def __make_request(method: str, url: str, headers: dict = None, debug: bool = False) -> Tuple[int, Any]:
        if headers is None:
            headers = {}
        async with request(method, url, headers = headers) as response:
            if debug:
                print(response.status, url)
            return response.status, await response.json()
    
    async def __make_api_request(self, url: str) -> Tuple[int, Any]:
        return await LoLAPI.__make_request(
            'GET',
            LoLAPI.__BASE_URL.format(self.region, url),
            {
                'X-Riot-Token': self.api_key
            }
        )
    
    @staticmethod
    async def create_object(response: Tuple[int, Any], object_class = None) -> Any:
        status, json_response = response
        if 200 <= status < 300:
            t = type(json_response)
            if not (object_class is None):
                if t == dict:
                    return object_class(**json_response)
                if t == list:
                    return list(map(lambda x: object_class(**x), json_response))
            return json_response
        else:
            return types.RiotApiError(**json_response.get('status', {}))
    
    # CHAMPION-MASTERY-V4
    async def get_masteries(self, encrypted_summoner_id: str) -> List[types.ChampionMasteryDto]:
        """
        /lol/champion-mastery/v4/champion-masteries/by-summoner/{encryptedSummonerId}
        :param encrypted_summoner_id:
        :return:
        """
        
        return await LoLAPI.create_object(
            await self.__make_api_request(
                f'/lol/champion-mastery/v4/champion-masteries/by-summoner/{encrypted_summoner_id}'
            ), types.ChampionMasteryDto
        )
    
    async def get_champion_mastery(self, encrypted_summoner_id: str, champion_id: int) -> types.ChampionMasteryDto:
        """
        /lol/champion-mastery/v4/champion-masteries/by-summoner/{encryptedSummonerId}/by-champion/{championId}
        :param encrypted_summoner_id:
        :param champion_id:
        :return:
        """
        
        return await LoLAPI.create_object(
            await self.__make_api_request(
                f'/lol/champion-mastery/v4/champion-masteries/by-summoner/{encrypted_summoner_id}/by-champion/{champion_id}'
            ), types.ChampionMasteryDto
        )
    
    async def get_mastery_score(self, encrypted_summoner_id: str) -> int:
        """
        /lol/champion-mastery/v4/scores/by-summoner/{encryptedSummonerId}
        :param encrypted_summoner_id:
        :return:
        """
        
        return await LoLAPI.create_object(
            await self.__make_api_request(f'/lol/champion-mastery/v4/scores/by-summoner/{encrypted_summoner_id}')
        )
    
    # CHAMPION-V3
    async def get_champion_rotation(self) -> types.ChampionInfo:
        """
        /lol/platform/v3/champion-rotations
        :return:
        """
        
        return await LoLAPI.create_object(
            await self.__make_api_request('/lol/platform/v3/champion-rotations'),
            types.ChampionInfo
        )
    
    # LEAGUE-V4
    async def get_league(self, encrypted_summoner_id: str) -> Set[types.LeagueEntryDTO]:
        """
        /lol/league/v4/entries/by-summoner/{encryptedSummonerId}
        :param encrypted_summoner_id:
        :return:
        """
        
        return set(
            await LoLAPI.create_object(
                await self.__make_api_request(f'/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}'),
                types.LeagueEntryDTO
            )
        )
    
    # LOL-STATUS-V3
    async def get_platform_data_v3(self) -> types.ShardStatus:
        """
        /lol/status/v4/platform-data
        :return:
        """
        
        return await LoLAPI.create_object(await self.__make_api_request('/lol/status/v3/shard-data'), types.ShardStatus)
    
    # LOL-STATUS-V4
    async def get_platform_data(self) -> types.PlatformDataDto:
        """
        /lol/status/v4/platform-data
        :return:
        """
        
        return await LoLAPI.create_object(
            await self.__make_api_request('/lol/status/v4/platform-data'),
            types.PlatformDataDto
        )
    
    # MATCH-V5
    async def get_matches_v5(self, puuid: str, start: int = 0, count: int = 20) -> List[str]:
        """
        /lol/match/v5/matches/by-puuid/{puuid}/ids
        :param puuid:
        :param start:
        :param count:
        :return:
        """
        
        return await LoLAPI.create_object(
            await LoLAPI.__make_request(
                'GET',
                LoLAPI.__BASE_URL.format(
                    self.v5_routing_value,
                    f'/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}'
                ),
                {
                    'X-Riot-Token': self.api_key
                }
            )
        )
    
    async def get_match_v5(self, match_id: str) -> types.MatchDto:
        """
        /lol/match/v5/matches/{matchId}
        :param match_id:
        :return:
        """
        
        return await LoLAPI.create_object(
            await LoLAPI.__make_request(
                'GET',
                LoLAPI.__BASE_URL.format(
                    self.v5_routing_value,
                    f'/lol/match/v5/matches/{match_id}'
                ),
                {
                    'X-Riot-Token': self.api_key
                }
            ), types.MatchDto
        )
    
    # SPECTATOR-V4
    async def get_active_games(self, encrypted_summoner_id: str) -> types.CurrentGameInfo:
        """
        /lol/spectator/v4/active-games/by-summoner/{encryptedSummonerId}
        :param encrypted_summoner_id:
        :return:
        """
        
        return await LoLAPI.create_object(
            await self.__make_api_request(f'/lol/spectator/v4/active-games/by-summoner/{encrypted_summoner_id}'),
            types.CurrentGameInfo
        )
    
    async def get_featured_games(self) -> types.FeaturedGames:
        """
        /lol/spectator/v4/featured-games
        :return:
        """
        
        return await LoLAPI.create_object(
            await self.__make_api_request('/lol/spectator/v4/featured-games'),
            types.FeaturedGames
        )
    
    # SUMMONER-V4
    async def get_summoner_by_encrypted_account_id(self, encrypted_account_id: str) -> types.SummonerDTO:
        """
        /lol/summoner/v4/summoners/by-account/{encryptedAccountId}
        :param encrypted_account_id:
        :return:
        """
        
        return await LoLAPI.create_object(
            await self.__make_api_request(f'/lol/summoner/v4/summoners/by-account/{encrypted_account_id}'),
            types.SummonerDTO
        )
    
    async def get_summoner_by_name(self, summoner_name: str) -> types.SummonerDTO:
        """
        /lol/summoner/v4/summoners/by-name/{summonerName}
        :param summoner_name:
        :return:
        """
        
        return await LoLAPI.create_object(
            await self.__make_api_request(f'/lol/summoner/v4/summoners/by-name/{quote_plus(summoner_name)}'),
            types.SummonerDTO
        )
    
    async def get_summoner_by_encrypted_puuid(self, encrypted_puuid: str) -> types.SummonerDTO:
        """
        /lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}
        :param encrypted_puuid:
        :return:
        """
        
        return await LoLAPI.create_object(
            await self.__make_api_request(f'/lol/summoner/v4/summoners/by-puuid/{encrypted_puuid}'),
            types.SummonerDTO
        )
    
    async def get_summoner_by_encrypted_summoner_id(self, encrypted_summoner_id: str) -> types.SummonerDTO:
        """
        /lol/summoner/v4/summoners/{encryptedSummonerId}
        :param encrypted_summoner_id:
        :return:
        """
        
        return await LoLAPI.create_object(
            await self.__make_api_request(f'/lol/summoner/v4/summoners/{encrypted_summoner_id}'),
            types.SummonerDTO
        )
    
    '''async def get_me(self) -> Dict[str, Any]:
        """
        /lol/summoner/v4/summoners/me
        :return:
        """

        return loads(await self.__make_request(f'/lol/summoner/v4/summoners/me'))'''
    
    # UTILS
    '''async def get_match_number(self, encrypted_account_id: str) -> int:
        return (await self.get_matches(encrypted_account_id, 101))['totalGames']

    async def get_nth_match(self, encrypted_account_id: str, n: int = 0) -> Dict[str, Any]:
        return await self.get_match((await self.get_matches(encrypted_account_id, n))['matches'][0]['gameId'])'''
    
    async def get_nth_match_v5(self, puuid: str, n: int = 0) -> types.MatchDto:
        return await self.get_match_v5((await self.get_matches_v5(puuid, n, 1) or [None])[0])
    
    '''async def get_first_match(self, encrypted_account_id: str) -> Dict[str, Any]:
        return await self.get_nth_match(encrypted_account_id, await self.get_match_number(encrypted_account_id) - 1)'''
    
    async def get_last_match(self, puuid: str) -> types.MatchDto:
        return await self.get_nth_match_v5(puuid)
    
    async def __get_league_type(self, encrypted_summoner_id: str, league_type: str = 'SOLO') -> types.LeagueEntryDTO:
        league_type = league_type.lower()
        for league in await self.get_league(encrypted_summoner_id):
            if league_type in league.queueType.lower():
                return league
    
    async def get_solo_league(self, encrypted_summoner_id: str) -> types.LeagueEntryDTO:
        return await self.__get_league_type(encrypted_summoner_id)
    
    async def get_flex_league(self, encrypted_summoner_id: str) -> types.LeagueEntryDTO:
        return await self.__get_league_type(encrypted_summoner_id, 'FLEX')
    
    @staticmethod
    def get_profile_icon_url(icon_id: int) -> str:
        return f'https://ddragon.leagueoflegends.com/cdn/{LoLAPI.__VERSION}/img/profileicon/{icon_id}.png'
    
    @staticmethod
    def get_champion_icon_url_from_id(champ_id: int, skin: int = 0, type: str = 'splash') -> str:
        return f'https://ddragon.leagueoflegends.com/cdn/img/champion/{type}/{LoLAPI.__CHAMP_ID_TO_CORRECT_NAME.get(champ_id)}_{skin}.jpg'
    
    @staticmethod
    def compute_champion_from_similar_name(search_name: str) -> Dict[str, Any]:
        max_ratio = 0
        matched_champ = None
        for champ_name in LoLAPI.__CHAMPS:
            ratio = fuzz.token_set_ratio(search_name, champ_name)
            if ratio > max_ratio:
                matched_champ = champ_name
                max_ratio = ratio
        return LoLAPI.__CHAMPS[matched_champ]
    
    @staticmethod
    def compute_language(search_language: str) -> str:
        max_ratio = 0
        matched_lang = None
        for language in LoLAPI.__LANGUAGES:
            ratio = fuzz.token_set_ratio(search_language, language)
            if ratio > max_ratio:
                matched_lang = language
                max_ratio = ratio
        return matched_lang
    
    @staticmethod
    def get_version() -> int:
        return LoLAPI.__VERSION
    
    @staticmethod
    def get_queue_description(queue_id: int) -> str:
        return LoLAPI.__QUEUES.get(queue_id, LoLAPI.__QUEUES[0])
    
    @staticmethod
    def get_champion_from_correct_name(name: str) -> Dict[str, Any]:
        return LoLAPI.__CHAMPS.get(name)
    
    @staticmethod
    def get_champion_from_id(champ_id: int) -> Dict[str, Any]:
        """
        :param champ_id: integer champion ID
        :return: short champion
        """
        return LoLAPI.get_champion_from_correct_name(LoLAPI.__CHAMP_ID_TO_CORRECT_NAME.get(champ_id))
    
    @staticmethod
    async def get_full_champion_from_correct_name(name: str, language: str):
        if language not in LoLAPI.__LANGUAGES:
            language = LoLAPI.compute_language(language)
        return (await LoLAPI.__make_request(
            'GET',
            f'https://ddragon.leagueoflegends.com/cdn/{LoLAPI.__VERSION}/data/{language}/champion/{name}.json'
        ))[1]['data'][name]
