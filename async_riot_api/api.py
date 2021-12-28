from typing import Any, Dict, List, Optional, Set, Tuple, Union
from json import loads
from fuzzywuzzy import fuzz
from aiohttp import request
from urllib.parse import quote_plus
import requests
from . import types


class LoLAPI:
    """
    Main class to interact with the API. Offers async methods corresponding to API methods and more.
    
    It is important to notice that this implementation is exception-free, not meaning that it's impossible to make mistake,
    but meaning that errors returned by the API are not raised as exceptions. Instead, they are returned as :class:`~types.RiotApiError`,
    containing information about the error.
    To distinguish between a successful response and an error, you can easily use the object as a boolean expression:
    
    .. code-block:: python
    
        summoner = await api.get_account_by_puuid(puuid)
        if not summoner:
            print(f'The request raised an error with status code {summoner.status_code}: {summoner.message}')
        else:
            print(summoner.to_string(sep = '|   '))
    
    :param api_key: your API token
    :type api_key: str
    :param region: region you want to use
    :type region: str
    :param routing_value: one among 'america', 'asia', 'esports' or 'europe'. Needed for some API calls, depends on region
    :type routing_value: str
    :param debug: if you want the LoLAPI object to print the url of every request made
    :type debug: bool
    """
    
    __BASE_URL: str = 'https://{}.api.riotgames.com{}'
    __VERSION: int = loads(requests.get('https://ddragon.leagueoflegends.com/api/versions.json').text)[0]
    __QUEUES: Dict[int, str] = {
        queue['queueId']: queue['description'].replace('games', '').strip() if queue['description'] else 'Custom'
        for queue in loads(requests.get('https://static.developer.riotgames.com/docs/lol/queues.json').text)
    }
    
    # correct_champion_name -> ShortChampionDD
    __CHAMPS: Dict[str, types.ShortChampionDD] = {name: types.ShortChampionDD(**value) for name, value in loads(
        requests.get(f'https://ddragon.leagueoflegends.com/cdn/{__VERSION}/data/en_US/champion.json').text
    )['data'].items()}
    
    # integer champion ID -> correct champion name
    __CHAMP_ID_TO_CORRECT_NAME: Dict[int, str] = {
        info.int_id: champ for champ, info in __CHAMPS.items()
    }
    __LANGUAGES: List[str] = loads(requests.get('https://ddragon.leagueoflegends.com/cdn/languages.json').text)
    __LANG_SHORT_TO_LONG: Dict[str, str] = {
        'it': 'it_IT',
        'en': 'en_US'
    }
    
    def __init__(self, api_key: str, region: str = 'euw1', routing_value: str = 'europe', debug: bool = False):
        self.api_key = api_key
        self.region = region
        self.routing_value = routing_value
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
            {'X-Riot-Token': self.api_key},
            debug = self.debug
        )
    
    @staticmethod
    async def __create_object(response: Tuple[int, Any], object_class = None) -> Any:
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
    
    # ACCOUNT-V1
    async def get_account_by_puuid(self, puuid: str) -> types.AccountDto:
        """
        To get an account given its puuid.
        
        Original method: /riot/account/v1/accounts/by-puuid/{puuid}
        
        :param puuid: puuid of the account
        :type puuid: str
        :return: account data
        :rtype: :class:`~types.AccountDto`
        """
        return await LoLAPI.__create_object(
            await LoLAPI.__make_request(
                'GET',
                LoLAPI.__BASE_URL.format(
                    self.routing_value,
                    f'/riot/account/v1/accounts/by-puuid/{puuid}'
                ),
                {'X-Riot-Token': self.api_key},
                debug = self.debug
            ),
            types.AccountDto,
        )
    
    async def get_account_by_game_name(self, game_name: str, tag_line: str) -> types.AccountDto:
        """
        To get an account given its name and tag line.
        
        Original method: /riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}
        
        :param game_name: in-game name of the account
        :type game_name: str
        :param tag_line: no documentation found
        :type tag_line: str
        :return: account data
        :rtype: :class:`~types.AccountDto`
        """
        return await LoLAPI.__create_object(
            await LoLAPI.__make_request(
                'GET',
                LoLAPI.__BASE_URL.format(
                    self.routing_value,
                    f'/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}'
                ),
                {'X-Riot-Token': self.api_key},
                debug = self.debug
            ),
            types.AccountDto,
        )
    
    async def get_active_shards(self, game: str, puuid: str) -> types.ActiveShardDto:
        """
        No documentation found.
        
        Original method: /riot/account/v1/active-shards/by-game/{game}/by-puuid/{puuid}
        
        :param game: one of 'val' or 'lol'
        :type game: str
        :param puuid: puuid of the account
        :type puuid: str
        :return: shard data
        :rtype: :class:`~types.ActiveShardDto`
        """
        return await LoLAPI.__create_object(
            await LoLAPI.__make_request(
                'GET',
                LoLAPI.__BASE_URL.format(
                    self.routing_value,
                    f'/riot/account/v1/active-shards/by-game/{game}/by-puuid/{puuid}'
                ),
                {'X-Riot-Token': self.api_key},
                debug = self.debug
            ),
            types.ActiveShardDto,
        )
    
    # CHAMPION-MASTERY-V4
    async def get_masteries(self, summoner_id: str) -> List[types.ChampionMasteryDto]:
        """
        
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(
                f'/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}'
            ),
            types.ChampionMasteryDto
        )
    
    async def get_champion_mastery(self, summoner_id: str, champion_id: int) -> types.ChampionMasteryDto:
        """
        /lol/champion-mastery/v4/champion-masteries/by-summoner/{encryptedSummonerId}/by-champion/{championId}
        :param summoner_id:
        :param champion_id:
        :return:
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(
                f'/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}/by-champion/{champion_id}'
            ), types.ChampionMasteryDto
        )
    
    async def get_mastery_score(self, summoner_id: str) -> int:
        """
        /lol/champion-mastery/v4/scores/by-summoner/{encryptedSummonerId}
        :param summoner_id:
        :return:
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/champion-mastery/v4/scores/by-summoner/{summoner_id}')
        )
    
    # CHAMPION-V3
    async def get_champion_rotation(self) -> types.ChampionInfo:
        """
        /lol/platform/v3/champion-rotations
        :return:
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request('/lol/platform/v3/champion-rotations'),
            types.ChampionInfo
        )
    
    # CLASH-V1
    async def get_clash_players_by_summoner_id(self, summoner_id: str) -> List[types.PlayerDto]:
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/clash/v1/players/by-summoner/{summoner_id}'),
            types.PlayerDto
        )
    
    async def get_clash_team_by_id(self, team_id: str) -> types.TeamDto:
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/clash/v1/teams/{team_id}'),
            types.TeamDto
        )
    
    async def get_clash_tournaments(self) -> List[types.TournamentDto]:
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/clash/v1/tournaments'),
            types.TournamentDto
        )
    
    async def get_clash_tournament_by_team_id(self, team_id: str) -> types.TournamentDto:
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/clash/v1/tournaments/by-team/{team_id}'),
            types.TournamentDto
        )
    
    async def get_clash_tournament_by_id(self, tournament_id: int) -> types.TournamentDto:
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/clash/v1/tournaments/{tournament_id}'),
            types.TournamentDto
        )
    
    # LEAGUE-V4
    async def get_challenger_leagues(self, queue: str) -> types.LeagueListDTO:
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/league/v4/challengerleagues/by-queue/{queue}'),
            types.LeagueListDTO
        )
    
    async def get_league(self, summoner_id: str) -> Set[types.LeagueEntryDTO]:
        """
        /lol/league/v4/entries/by-summoner/{encryptedSummonerId}
        :param summoner_id:
        :return:
        """
        
        return set(
            await LoLAPI.__create_object(
                await self.__make_api_request(f'/lol/league/v4/entries/by-summoner/{summoner_id}'),
                types.LeagueEntryDTO
            )
        )
    
    async def get_summoners_by_league(self, queue: str, tier: str, division: str, page: int = 1) -> Set[
        types.LeagueEntryDTO]:
        return set(
            await LoLAPI.__create_object(
                await self.__make_api_request(f'/lol/league/v4/entries/{queue}/{tier}/{division}?page={page}'),
                types.LeagueEntryDTO
            )
        )
    
    async def get_grand_master_leagues(self, queue: str) -> types.LeagueListDTO:
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/league/v4/grandmasterleagues/by-queue/{queue}'),
            types.LeagueListDTO
        )
    
    async def get_leagues(self, league_id: str) -> types.LeagueListDTO:
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/league/v4/leagues/{league_id}'),
            types.LeagueListDTO
        )
    
    async def get_master_leagues(self, queue: str) -> types.LeagueListDTO:
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/league/v4/masterleagues/by-queue/{queue}'),
            types.LeagueListDTO
        )
    
    # LOL-STATUS-V3
    async def get_platform_data_v3(self) -> types.ShardStatus:
        """
        /lol/status/v4/platform-data
        :return:
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request('/lol/status/v3/shard-data'),
            types.ShardStatus
        )
    
    # LOL-STATUS-V4
    async def get_platform_data(self) -> types.PlatformDataDto:
        """
        /lol/status/v4/platform-data
        :return:
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request('/lol/status/v4/platform-data'),
            types.PlatformDataDto
        )
    
    # LOR-MATCH-V1
    async def get_lor_matches(self, puuid: str) -> List[str]:
        return await LoLAPI.__create_object(
            await LoLAPI.__make_request(
                'GET',
                LoLAPI.__BASE_URL.format(self.routing_value, f'/lor/match/v1/matches/by-puuid/{puuid}/ids'),
                {'X-Riot-Token': self.api_key},
                debug = self.debug
            )
        )
    
    async def get_lor_match(self, match_id: str) -> types.LorMatchDto:
        return await LoLAPI.__create_object(
            await LoLAPI.__make_request(
                'GET',
                LoLAPI.__BASE_URL.format(self.routing_value, f'/lor/match/v1/matches/{match_id}'),
                {'X-Riot-Token': self.api_key},
                debug = self.debug
            ),
            types.LorMatchDto
        )
    
    # LOR-RANKED-V1
    async def get_lor_leaderboards(self) -> types.LorLeaderboardDto:
        return await LoLAPI.__create_object(
            await LoLAPI.__make_request(
                'GET',
                LoLAPI.__BASE_URL.format(self.routing_value, f'/lor/ranked/v1/leaderboards'),
                {'X-Riot-Token': self.api_key},
                debug = self.debug
            ),
            types.LorLeaderboardDto
        )
    
    # LOR-STATUS-V1
    async def get_lor_status(self) -> types.PlatformDataDto:
        return await LoLAPI.__create_object(
            await LoLAPI.__make_request(
                'GET',
                LoLAPI.__BASE_URL.format(self.routing_value, f'/lor/status/v1/platform-data'),
                {'X-Riot-Token': self.api_key},
                debug = self.debug
            ),
            types.PlatformDataDto
        )
    
    # MATCH-V5
    async def get_matches(self, puuid: str, *, startTime: Optional[int] = None, endTime: Optional[int] = None,
                          queue: Optional[int] = None, type: Optional[str] = None, start: int = 0,
                          count: int = 20) -> List[str]:
        """
        /lol/match/v5/matches/by-puuid/{puuid}/ids
        :param puuid:
        :param queue:
        :param startTime:
        :param endTime:
        :param type:
        :param start:
        :param count:
        :return:
        """
        
        url = f'/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}'
        if startTime:
            url += f'&startTime={startTime}'
        if endTime:
            url += f'&endTime={endTime}'
        if queue:
            url += f'&queue={queue}'
        if type:
            url += f'&type={type}'
        return await LoLAPI.__create_object(
            await LoLAPI.__make_request(
                'GET',
                LoLAPI.__BASE_URL.format(self.routing_value, url),
                {'X-Riot-Token': self.api_key},
                debug = self.debug
            )
        )
    
    async def get_match(self, match_id: str) -> types.MatchDto:
        """
        /lol/match/v5/matches/{matchId}
        :param match_id:
        :return:
        """
        
        return await LoLAPI.__create_object(
            await LoLAPI.__make_request(
                'GET',
                LoLAPI.__BASE_URL.format(
                    self.routing_value,
                    f'/lol/match/v5/matches/{match_id}'
                ),
                {'X-Riot-Token': self.api_key},
                debug = self.debug
            ),
            types.MatchDto,
        )
    
    async def get_timeline(self, match_id: str) -> types.MatchTimelineDto:
        return await LoLAPI.__create_object(
            await LoLAPI.__make_request(
                'GET',
                LoLAPI.__BASE_URL.format(
                    self.routing_value,
                    f'/lol/match/v5/matches/{match_id}/timeline'
                ),
                {'X-Riot-Token': self.api_key},
                debug = self.debug
            ),
            types.MatchTimelineDto,
        )
    
    # SPECTATOR-V4
    async def get_active_games(self, summoner_id: str) -> types.CurrentGameInfo:
        """
        /lol/spectator/v4/active-games/by-summoner/{encryptedSummonerId}
        :param summoner_id:
        :return:
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/spectator/v4/active-games/by-summoner/{summoner_id}'),
            types.CurrentGameInfo
        )
    
    async def get_featured_games(self) -> types.FeaturedGames:
        """
        /lol/spectator/v4/featured-games
        :return:
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request('/lol/spectator/v4/featured-games'),
            types.FeaturedGames
        )
    
    # SUMMONER-V4
    async def get_summoner_by_account_id(self, account_id: str) -> types.SummonerDTO:
        """
        /lol/summoner/v4/summoners/by-account/{encryptedAccountId}
        :param account_id:
        :return:
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/summoner/v4/summoners/by-account/{account_id}'),
            types.SummonerDTO
        )
    
    async def get_summoner_by_name(self, summoner_name: str) -> types.SummonerDTO:
        """
        /lol/summoner/v4/summoners/by-name/{summonerName}
        :param summoner_name:
        :return:
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/summoner/v4/summoners/by-name/{quote_plus(summoner_name)}'),
            types.SummonerDTO
        )
    
    async def get_summoner_by_puuid(self, puuid: str) -> types.SummonerDTO:
        """
        /lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}
        :param puuid:
        :return:
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/summoner/v4/summoners/by-puuid/{puuid}'),
            types.SummonerDTO
        )
    
    async def get_summoner_by_summoner_id(self, summoner_id: str) -> types.SummonerDTO:
        """
        /lol/summoner/v4/summoners/{encryptedSummonerId}
        :param summoner_id:
        :return:
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/summoner/v4/summoners/{summoner_id}'),
            types.SummonerDTO
        )
    
    '''async def get_me(self) -> Dict[str, Any]:
        """
        /lol/summoner/v4/summoners/me
        :return:
        """

        return loads(await self.__make_request(f'/lol/summoner/v4/summoners/me'))'''
    
    # UTILS
    '''async def get_match_number(self, account_id: str) -> int:
        return (await self.get_matches(account_id, 101))['totalGames']

    async def get_nth_match(self, account_id: str, n: int = 0) -> Dict[str, Any]:
        return await self.get_match((await self.get_matches(account_id, n))['matches'][0]['gameId'])'''
    
    async def get_nth_match(self, puuid: str, n: int = 0) -> types.MatchDto:
        return await self.get_match((await self.get_matches(puuid, start = n, count = 1) or [None])[0])
    
    '''async def get_first_match(self, account_id: str) -> Dict[str, Any]:
        return await self.get_nth_match(account_id, await self.get_match_number(account_id) - 1)'''
    
    async def get_last_match(self, puuid: str) -> types.MatchDto:
        return await self.get_nth_match(puuid)
    
    async def __get_league_type(self, summoner_id: str, league_type: str) -> Union[
        types.LeagueEntryDTO, types.RiotApiError]:
        league_type = league_type.lower()
        leagues = await self.get_league(summoner_id)
        if type(leagues) != set:
            return leagues
        for league in leagues:
            if league_type in league.queueType.lower():
                return league
    
    async def get_solo_league(self, summoner_id: str) -> Optional[types.LeagueEntryDTO]:
        return await self.__get_league_type(summoner_id, 'SOLO')
    
    async def get_flex_league(self, summoner_id: str) -> Optional[types.LeagueEntryDTO]:
        return await self.__get_league_type(summoner_id, 'FLEX')
    
    @staticmethod
    def get_profile_icon_url(icon_id: int) -> str:
        return f'https://ddragon.leagueoflegends.com/cdn/{LoLAPI.__VERSION}/img/profileicon/{icon_id}.png'
    
    @staticmethod
    def get_champion_icon_url_from_id(champ_id: int, skin: int = 0, type: str = 'splash') -> str:
        return f'https://ddragon.leagueoflegends.com/cdn/img/champion/{type}/{LoLAPI.__CHAMP_ID_TO_CORRECT_NAME.get(int(champ_id))}_{skin}.jpg'
    
    @staticmethod
    def compute_champion_from_similar_name(search_name: str) -> types.ShortChampionDD:
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
    def get_champion_from_correct_name(name: str) -> types.ShortChampionDD:
        return LoLAPI.__CHAMPS.get(name)
    
    @staticmethod
    def get_champion_from_id(champ_id: int) -> types.ShortChampionDD:
        """
        :param champ_id: integer champion ID
        :return: short champion
        """
        return LoLAPI.get_champion_from_correct_name(LoLAPI.__CHAMP_ID_TO_CORRECT_NAME.get(champ_id))
    
    @staticmethod
    async def get_full_champion_from_correct_name(name: str, language: str) -> types.ChampionDD:
        if language not in LoLAPI.__LANGUAGES:
            language = LoLAPI.compute_language(language)
        return types.ChampionDD(
            **((await LoLAPI.__make_request(
                'GET',
                f'https://ddragon.leagueoflegends.com/cdn/{LoLAPI.__VERSION}/data/{language}/champion/{name}.json'
            ))[1]['data'][name])
        )
    
    @staticmethod
    def get_map_icon_url(map_id: int):
        return f'https://ddragon.leagueoflegends.com/cdn/6.8.1/img/map/map{map_id}.png'
