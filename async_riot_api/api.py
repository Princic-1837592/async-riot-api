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
            print(f'Error with status code {summoner.status_code}: {summoner.message}')
        else:
            print(summoner.to_string(sep = '|   '))
    
    Another important thing to know is that some methods are simple functions, not coroutines,
    meaning that they only work with offline data without making any request. They are usually static methods.
    
    :param api_key: your API token
    :param region: region you want to use
    :param routing_value: one among 'AMERICA', 'ASIA', 'ESPORTS', 'EUROPE' or 'SEA. Needed for some API calls, depends on region
    :param debug: if you want the LoLAPI object to print the url of every request made
    :type api_key: str
    :type region: str
    :type routing_value: str
    :type debug: bool
    """
    
    __BASE_URL: str = 'https://{}.api.riotgames.com{}'
    
    __VERSION: int = loads(requests.get('https://ddragon.leagueoflegends.com/api/versions.json').text)[0]
    
    __QUEUES: Dict[int, types.QueueDD] = {
        queue['queueId']: types.QueueDD(**queue) for queue in
        loads(requests.get('https://static.developer.riotgames.com/docs/lol/queues.json').text)
    }
    __QUEUES[-1] = types.QueueDD(-1, 'Unknown', 'Unknown', 'Wrong queue_id')
    
    # correct_champion_name -> ShortChampionDD
    __CHAMPS: Dict[str, types.ShortChampionDD] = {name: types.ShortChampionDD(**value) for name, value in loads(
        requests.get(f'https://ddragon.leagueoflegends.com/cdn/{__VERSION}/data/en_US/champion.json').text
    )['data'].items()}
    
    # integer champion ID -> correct champion name
    __CHAMP_ID_TO_CORRECT_NAME: Dict[int, str] = {
        info.int_id: info.id for info in __CHAMPS.values()
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
        
        `Original method <https://developer.riotgames.com/apis#account-v1/GET_getByPuuid>`_.
        
        :param puuid: puuid of the account
        :return: account data
        :type puuid: str
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
        
        `Original method <https://developer.riotgames.com/apis#account-v1/GET_getByRiotId>`_.
        
        :param game_name: in-game name of the account
        :param tag_line: no documentation found
        :return: account data
        :type game_name: str
        :type tag_line: str
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
        
        `Original method <https://developer.riotgames.com/apis#account-v1/GET_getActiveShard>`_.
        
        :param game: one of 'val' or 'lor'
        :param puuid: puuid of the account
        :return: shard data
        :type game: str
        :type puuid: str
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
        Get the list of masteries for a summoner.
        
        `Original method <https://developer.riotgames.com/apis#champion-mastery-v4/GET_getAllChampionMasteries>`_.
        
        :param summoner_id: summoner ID
        :return: list of masteries for the given summoner
        :type summoner_id: str
        :rtype: List[:class:`~types.ChampionMasteryDto`]
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(
                f'/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}'
            ),
            types.ChampionMasteryDto
        )
    
    async def get_champion_mastery(self, summoner_id: str, champion_id: int) -> types.ChampionMasteryDto:
        """
        Get a specific champion mastery for the given summoner.
        
        `Original method <https://developer.riotgames.com/apis#champion-mastery-v4/GET_getChampionMastery>`_.
        
        :param summoner_id:
        :param champion_id:
        :return: champion mastery for given summoner and champion
        :type summoner_id: str
        :type champion_id: int
        :rtype: :class:`~types.ChampionMasteryDto`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(
                f'/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}/by-champion/{champion_id}'
            ), types.ChampionMasteryDto
        )
    
    async def get_mastery_score(self, summoner_id: str) -> int:
        """
        Get the total mastery score of a summoner. Mastery score is given by the sum of individual champion mastery levels.
        
        `Original method <https://developer.riotgames.com/apis#champion-mastery-v4/GET_getChampionMasteryScore>`_.
        
        :param summoner_id:
        :return: mastery score of the given summoner
        :type summoner_id: str
        :rtype: int
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/champion-mastery/v4/scores/by-summoner/{summoner_id}')
        )
    
    # CHAMPION-V3
    async def get_champion_rotation(self) -> types.ChampionInfo:
        """
        Get champion rotations, including free-to-play and low-level free-to-play rotations.
        
        `Original method <https://developer.riotgames.com/apis#champion-v3/GET_getChampionInfo>`_.
        
        :return: information about champion rotations
        :rtype: :class:`~types.ChampionInfo`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request('/lol/platform/v3/champion-rotations'),
            types.ChampionInfo
        )
    
    # CLASH-V1
    async def get_clash_players_by_summoner_id(self, summoner_id: str) -> List[types.PlayerDto]:
        """
        Get a list of active Clash players for a given summoner ID.
        If a summoner registers for multiple tournaments at the same time (e.g., Saturday and Sunday)
        then both registrations would appear in this list.
        
        `Original method <https://developer.riotgames.com/apis#clash-v1/GET_getPlayersBySummoner>`_.
        
        :param summoner_id:
        :return: list of players
        :type summoner_id: str
        :rtype: List[:class:`~types.PlayerDto`]
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/clash/v1/players/by-summoner/{summoner_id}'),
            types.PlayerDto
        )
    
    async def get_clash_team_by_id(self, team_id: str) -> types.ClashTeamDto:
        """
        Get a clash team by its ID.
        
        `Original method <https://developer.riotgames.com/apis#clash-v1/GET_getTeamById>`_.
        
        :param team_id:
        :return: information about the team
        :type team_id: str
        :rtype: :class:`~types.TeamDto`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/clash/v1/teams/{team_id}'),
            types.ClashTeamDto
        )
    
    async def get_clash_tournaments(self) -> List[types.TournamentDto]:
        """
        Get all active or upcoming tournaments.
        
        `Original method <https://developer.riotgames.com/apis#clash-v1/GET_getTournaments>`_.
        
        :return: list of tournaments
        :rtype: List[:class:`~types.TournamentDto`]
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/clash/v1/tournaments'),
            types.TournamentDto
        )
    
    async def get_clash_tournament_by_team_id(self, team_id: str) -> types.TournamentDto:
        """
        Get tournament by team ID.
        
        `Original method <https://developer.riotgames.com/apis#clash-v1/GET_getTournamentByTeam>`_.
        
        :param team_id:
        :return: information about tournament
        :type team_id: str
        :rtype: :class:`~types.TournamentDto`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/clash/v1/tournaments/by-team/{team_id}'),
            types.TournamentDto
        )
    
    async def get_clash_tournament_by_id(self, tournament_id: int) -> types.TournamentDto:
        """
        Get info about a clash tournament by its ID.
        
        `Original method <https://developer.riotgames.com/apis#clash-v1/GET_getTournamentById>`_.
        
        :param tournament_id:
        :return: information about the tournament
        :type tournament_id: int
        :rtype: :class:`~types.TournamentDto`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/clash/v1/tournaments/{tournament_id}'),
            types.TournamentDto
        )
    
    # LEAGUE-EXP-V4
    async def get_summoners_by_league_exp(self, queue: str, tier: str, division: str, page: int = 1) -> Set[
        types.LeagueEntryDTO]:
        """
        This is an experimental (and personally untested) endpoint added as a duplicate of
        :meth:`~async_riot_api.LoLAPI.get_summoners_by_league`,
        but it also supports the apex tiers (Challenger, Grandmaster, and Master).
        
        `Original method <https://developer.riotgames.com/apis#league-exp-v4/GET_getLeagueEntries>`_..
        
        :param queue: one among 'RANKED_SOLO_5x5', 'RANKED_TFT', 'RANKED_FLEX_SR' or 'RANKED_FLEX_TT'
        :param tier: rank tier, between 'IRON' and 'CHALLENGER'
        :param division: rank division, between 'I' and 'IV' (in roman numbers)
        :param page: page to select, starting from 1. Limited based on the number of entries, it's suggested to iter until results are found
        :return: set of summoners for the requested queue, tier and division
        :type queue: str
        :type tier: str
        :type division: str
        :type page: int
        :rtype: Set[:class:`~types.LeagueEntryDTO`]
        """
        
        return set(
            await LoLAPI.__create_object(
                await self.__make_api_request(f'/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={page}'),
                types.LeagueEntryDTO
            )
        )
    
    # LEAGUE-V4
    async def get_challenger_leagues(self, queue: str) -> types.LeagueListDTO:
        """
        Get the list of challengers.
        
        `Original method <https://developer.riotgames.com/apis#league-v4/GET_getChallengerLeague>`_.
        
        :param queue: one among 'RANKED_SOLO_5x5', 'RANKED_FLEX_SR' or 'RANKED_FLEX_TT'
        :return: set of challengers
        :type queue: str
        :rtype: :class:`~types.LeagueListDTO`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/league/v4/challengerleagues/by-queue/{queue}'),
            types.LeagueListDTO
        )
    
    async def get_league(self, summoner_id: str) -> Set[types.LeagueEntryDTO]:
        """
        Get the set of league entries for a given summoner.
        
        `Original method <https://developer.riotgames.com/apis#league-v4/GET_getLeagueEntriesForSummoner>`_.
        
        :param summoner_id:
        :return: information about their ranks in every queue
        :type summoner_id: str
        :rtype: Set[:class:`~types.LeagueEntryDTO`]
        """
        
        return set(
            await LoLAPI.__create_object(
                await self.__make_api_request(f'/lol/league/v4/entries/by-summoner/{summoner_id}'),
                types.LeagueEntryDTO
            )
        )
    
    async def get_summoners_by_league(self, queue: str, tier: str, division: str, page: int = 1) -> Set[
        types.LeagueEntryDTO]:
        """
        Get the list of summoners that are currently in the given rank of the given queue. Only supports non-apex tiers.
        To get information about apex tiers, look at :meth:`~async_riot_api.LoLAPI.get_summoners_by_league_exp`.
        
        `Original method <https://developer.riotgames.com/apis#league-v4/GET_getLeagueEntries>`_.
        
        :param queue: one among 'RANKED_SOLO_5x5', 'RANKED_FLEX_SR' or 'RANKED_FLEX_TT'
        :param tier: rank tier, between 'IRON' and 'DIAMOND'
        :param division: rank division, between 'I' and 'IV' (in roman numbers)
        :param page: page to select, starting from 1. Limited based on the number of entries, it's suggested to iter until results are found
        :return: set of summoners for the requested queue, tier and division
        :type queue: str
        :type tier: str
        :type division: str
        :type page: int
        :rtype: Set[:class:`~types.LeagueEntryDTO`]
        """
        
        return set(
            await LoLAPI.__create_object(
                await self.__make_api_request(f'/lol/league/v4/entries/{queue}/{tier}/{division}?page={page}'),
                types.LeagueEntryDTO
            )
        )
    
    async def get_grand_master_leagues(self, queue: str) -> types.LeagueListDTO:
        """
        Same as :meth:`~async_riot_api.LoLAPI.get_challenger_leagues`, but for grand masters.
        
        `Original method <https://developer.riotgames.com/apis#league-v4/GET_getGrandmasterLeague>`_.
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/league/v4/grandmasterleagues/by-queue/{queue}'),
            types.LeagueListDTO
        )
    
    async def get_leagues(self, league_id: str) -> types.LeagueListDTO:
        """
        Get the list of summoners in the given league by its ID.
        
        `Original method <https://developer.riotgames.com/apis#league-v4/GET_getLeagueById>`_.
        
        :param league_id:
        :return: list of summoners currently in the given league
        :type league_id: str
        :rtype: :class:`~types.LeagueListDTO`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/league/v4/leagues/{league_id}'),
            types.LeagueListDTO
        )
    
    async def get_master_leagues(self, queue: str) -> types.LeagueListDTO:
        """
        Same as :meth:`~async_riot_api.LoLAPI.get_challenger_leagues`, but for masters.
        
        `Original method <https://developer.riotgames.com/apis#league-v4/GET_getGrandmasterLeague>`_.
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/league/v4/masterleagues/by-queue/{queue}'),
            types.LeagueListDTO
        )
    
    # LOL-STATUS-V3
    async def get_platform_data_v3(self) -> types.ShardStatus:
        """
        ``DEPRECATED`` Get information about LoL server status.
        
        `Original method <https://developer.riotgames.com/apis#lol-status-v3/GET_getShardData>`_.
        
        :return: the current server status
        :rtype: :class:`~types.ShardStatus`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request('/lol/status/v3/shard-data'),
            types.ShardStatus
        )
    
    # LOL-STATUS-V4
    async def get_platform_data(self) -> types.PlatformDataDto:
        """
        Get information about LoL server status.
        
        `Original method <https://developer.riotgames.com/apis#lol-status-v4/GET_getPlatformData>`_.
        
        :return: the current LoL server status
        :rtype: :class:`~types.PlatformDataDto`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request('/lol/status/v4/platform-data'),
            types.PlatformDataDto
        )
    
    # LOR-MATCH-V1
    async def get_lor_matches(self, puuid: str) -> List[str]:
        """
        Get the list of LoR matches played by the given summoner. Often used before :meth:`~async_riot_api.LoLAPI.get_lor_match`.
        
        `Original method <https://developer.riotgames.com/apis#lor-match-v1/GET_getMatchIdsByPUUID>`_.
        
        :param puuid:
        :return: list of match IDs sorted by recent
        :type puuid: str
        :rtype: List[str]
        """
        
        return await LoLAPI.__create_object(
            await LoLAPI.__make_request(
                'GET',
                LoLAPI.__BASE_URL.format(self.routing_value, f'/lor/match/v1/matches/by-puuid/{puuid}/ids'),
                {'X-Riot-Token': self.api_key},
                debug = self.debug
            )
        )
    
    async def get_lor_match(self, match_id: str) -> types.LorMatchDto:
        """
        Get information about the given LoR match. Often used after :meth:`~async_riot_api.LoLAPI.get_lor_matches`.
        
        `Original method <https://developer.riotgames.com/apis#lor-match-v1/GET_getMatch>`_.
        
        :param match_id:
        :return: useful information about the given LoR match and its players
        :type match_id: str
        :rtype: :class:`~types.LorMatchDto`
        """
        
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
        """
        Get the list of players in Master tier.
        
        `Original method <https://developer.riotgames.com/apis#lor-ranked-v1/GET_getLeaderboards>`_.
        
        :return: players in LoR Master tier
        :rtype: :class:`~types.LorLeaderboardDto`
        """
        
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
        """
        Get information about LoR servers status.
        
        `Original method <https://developer.riotgames.com/apis#lor-status-v1/GET_getPlatformData>`_.
        
        :return: the current LoR server status
        :rtype: :class:`~types.PlatformDataDto`
        """
        
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
        Get the list of LoL matches played by the given summoner. Often used before :meth:`~async_riot_api.LoLAPI.get_match`.
        Allows filtering by start/end time, queue and type of match.
        
        `Original method <https://developer.riotgames.com/apis#match-v5/GET_getMatchIdsByPUUID>`_.
        
        :param puuid:
        :param startTime: epoch timestamp in seconds. The matchlist started storing timestamps on June 16th, 2021.
            Any matches played before June 16th, 2021 won't be included in the results if the startTime filter is set
        :param endTime: epoch timestamp in seconds
        :param queue: queue filter for the list. Queue IDs can be found `here <https://static.developer.riotgames.com/docs/lol/queues.json>`_.
            Queue and type parameters are mutually inclusive
        :param type: one among 'ranked', 'normal', 'tourney' or 'tutorial'
        :param start: start index, starting from 0. Default 0
        :param count: number of match IDs to return. Must be in the range 0-100. Default 20
        :return: list of match IDs sorted by recent
        :type puuid: str
        :type startTime: int
        :type endTime: int
        :type queue: int
        :type type: str
        :type start: int
        :type count: int
        :rtype: List[str]
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
        Get information about the given LoL match. Often used after :meth:`~async_riot_api.LoLAPI.get_matches`.
        
        `Original method <https://developer.riotgames.com/apis#match-v5/GET_getMatch>`_.
        
        :param match_id:
        :return: useful information about the given LoR match and its players
        :type match_id: str
        :rtype: :class:`~types.MatchDto`
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
        """
        Get additional information about a match, ordered by time, organized in "frames".
        This kind of response contains information about items bought, skills unlocked, summoners position and more.
        Unfortunately on the original doc this method is not documented at all. Not even the return type is documented except for its name,
        so anything about this method comes from experimentation.
        
        `Original method <https://developer.riotgames.com/apis#match-v5/GET_getTimeline>`_.
        
        :param match_id:
        :return: more data about the match, ordered by time
        :type match_id: str
        :rtype: :class:`~types.MatchTimelineDto`
        """
        
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
        Get information about the active game played by the given summoner.
        
        ``IMPORTANT`` This method returns a :class:`~types.RiotApiError` if the summoner is not in a game.
        
        `Original method <https://developer.riotgames.com/apis#spectator-v4/GET_getCurrentGameInfoBySummoner>`_.
        
        :param summoner_id:
        :return: information about the current match and its players, if exists
        :type summoner_id: str
        :rtype: :class:`~types.CurrentGameInfo`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/spectator/v4/active-games/by-summoner/{summoner_id}'),
            types.CurrentGameInfo
        )
    
    async def get_featured_games(self) -> types.FeaturedGames:
        """
        Get a list of games that are currently being played. It is not clear to me what are the criteria for a game
        to be listed here, and I haven't found anything on the documentation. Anyway, this method could be useful
        for those who need to harvest a large amount of data from real matches.
        
        `Original method <https://developer.riotgames.com/apis#spectator-v4/GET_getFeaturedGames>`_.
        
        :return: games that are currently being played
        :rtype: :class:`~types.FeaturedGames`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request('/lol/spectator/v4/featured-games'),
            types.FeaturedGames
        )
    
    # SUMMONER-V4
    async def get_summoner_by_account_id(self, account_id: str) -> types.SummonerDTO:
        """
        Get information about a summoner by its account ID. You can get an account ID using
        :meth:`~async_riot_api.LoLAPI.get_summoner_by_name`.
        
        `Original method <https://developer.riotgames.com/apis#summoner-v4/GET_getByAccountId>`_.
        
        :param account_id:
        :return: basic information about the summoner
        :type account_id: str
        :rtype: :class:`~types.SummonerDTO`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/summoner/v4/summoners/by-account/{account_id}'),
            types.SummonerDTO
        )
    
    async def get_summoner_by_name(self, summoner_name: str) -> types.SummonerDTO:
        """
        Probably the first method you will need to call at the beginning of any program involving Riot Games API.
        This method allows accessing basic information about a summoner given its name. With this information you will
        be able to use any other method requiring a summoner ID, account ID or puuid.
        
        `Original method <https://developer.riotgames.com/apis#summoner-v4/GET_getBySummonerName>`_.
        
        :param summoner_name: name of the summoner you are looking for
        :return: basic information about the summoner
        :type summoner_name: str
        :rtype: :class:`~types.SummonerDTO`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/summoner/v4/summoners/by-name/{quote_plus(summoner_name)}'),
            types.SummonerDTO
        )
    
    async def get_summoner_by_puuid(self, puuid: str) -> types.SummonerDTO:
        """
        Get information about a summoner by its puuid. You can get a puuid using
        :meth:`~async_riot_api.LoLAPI.get_summoner_by_name`.
        
        `Original method <https://developer.riotgames.com/apis#summoner-v4/GET_getByPUUID>`_.
        
        :param puuid:
        :return: basic information about the summoner
        :type puuid: str
        :rtype: :class:`~types.SummonerDTO`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/summoner/v4/summoners/by-puuid/{puuid}'),
            types.SummonerDTO
        )
    
    async def get_summoner_by_summoner_id(self, summoner_id: str) -> types.SummonerDTO:
        """
        Get information about a summoner by its summoner ID. You can get a summoner ID using
        :meth:`~async_riot_api.LoLAPI.get_summoner_by_name`.
        
        `Original method <https://developer.riotgames.com/apis#summoner-v4/GET_getByPUUID>`_.
        
        :param summoner_id:
        :return: basic information about the summoner
        :type summoner_id: str
        :rtype: :class:`~types.SummonerDTO`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/summoner/v4/summoners/{summoner_id}'),
            types.SummonerDTO
        )
    
    # UTILS
    async def get_nth_match(self, puuid: str, n: int = 0) -> Optional[types.MatchDto]:
        """
        Directly get information about a summoner's match given its index, starting from 0.
        This is just a shorcut for :meth:`~async_riot_api.LoLAPI.get_matches` and :meth:`~async_riot_api.LoLAPI.get_match`.
        
        :param puuid: puuid of the summoner
        :param n: index of the match, starting from 0. Default 0
        :return: information about the match, if exists. None otherwise
        :type puuid: str
        :type n: int
        :rtype: Optional[:class:`~types.MatchDto`]
        """
        
        return await self.get_match((await self.get_matches(puuid, start = n, count = 1) or [None])[0])
    
    async def get_last_match(self, puuid: str) -> Optional[types.MatchDto]:
        """
        Directly get information about a summoner's last match.
        This is just a shortcut for :meth:`~async_riot_api.LoLAPI.get_nth_match`.
        
        :param puuid:
        :return: same as :meth:`~async_riot_api.LoLAPI.get_nth_match`
        :type puuid: str
        :rtype: Optional[:class:`~types.MatchDto`]
        """
        
        return await self.get_nth_match(puuid)
    
    async def __get_league_type(self, summoner_id: str, league_type: str) -> Union[
        types.LeagueEntryDTO, types.RiotApiError]:
        league_type = league_type.lower()
        leagues = await self.get_league(summoner_id)
        if type(leagues) != set:
            return leagues
        for league in leagues:
            if league_type == league.queueType.lower():
                return league
    
    async def get_solo_league(self, summoner_id: str) -> Optional[types.LeagueEntryDTO]:
        """
        Directly get information about a summoner's SOLO rank.
        
        :param summoner_id:
        :return: given summoner's SOLO rank, if exists.
        :type summoner_id: str
        :rtype: :class:`~types.LeagueEntryDTO`
        """
        
        return await self.__get_league_type(summoner_id, 'RANKED_SOLO_5x5')
    
    async def get_flex_league(self, summoner_id: str) -> Optional[types.LeagueEntryDTO]:
        """
        Same as :meth:`~async_riot_api.LoLAPI.get_solo_league`, but FLEX.
        
        :param summoner_id:
        :return: given summoner's FLEX rank, if exists.
        :type summoner_id: str
        :rtype: :class:`~types.LeagueEntryDTO`
        """
        
        return await self.__get_league_type(summoner_id, 'RANKED_FLEX_SR')
    
    @staticmethod
    def get_profile_icon_url(icon_id: int) -> str:
        """
        Returns the url to the given icon.
        
        ``IMPORTANT``: no check will be made about data existence, meaning that passing a wrong icon_id will simply result
        in a broken url. No error will be raised.
        
        :param icon_id:
        :return: url to the icon
        :type icon_id: int
        :rtype: str
        """
        
        return f'https://ddragon.leagueoflegends.com/cdn/{LoLAPI.__VERSION}/img/profileicon/{icon_id}.png'
    
    @staticmethod
    def get_champion_image_url_from_id(champ_id: int, skin: int = 0, type: str = 'splash') -> str:
        """
        Returns the url to the image for the given champion, skin and type.
        
        ``IMPORTANT``: no check will be made about data existence, meaning that passing a wrong champ_id, skin or type will simply result
        in a broken url. No error will be raised.
        
        :param champ_id: champion ID, corresponding to ``ShortChampionDD.int_id``
        :param skin: number of the requested skin, starting from 0 for the default skin. Default 0
        :param type: type of image. Can be 'splash' or 'loading'. Default 'splash'
        :return: url to the image
        :type champ_id: int
        :type skin: int
        :type type: str
        :rtype: str
        """
        return f'https://ddragon.leagueoflegends.com/cdn/img/champion/{type}/{LoLAPI.__CHAMP_ID_TO_CORRECT_NAME.get(int(champ_id))}_{skin}.jpg'
    
    @staticmethod
    def compute_champion_from_similar_name(search_name: str) -> types.ShortChampionDD:
        """
        Computes the most similar champion to the given name. The similarity computation
        is made using `this library <https://pypi.org/project/fuzzywuzzy/>`_.
        
        :param search_name: name to search
        :return: champion whose name is the most similar to the given one
        :type search_name: str
        :rtype: :class:`~types.ShortChampionDD`
        """
        
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
        """
        Computes the most similar language available from `this list <https://ddragon.leagueoflegends.com/cdn/languages.json>`_.
        The similarity computation is made using `this library <https://pypi.org/project/fuzzywuzzy/>`_.
        
        :param search_language: language to search
        :return: most similar language
        :type search_language: str
        :rtype: str
        """
        
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
        """
        Get the latest version of the game.
        
        :return: latest version of the game
        :rtype: int
        """
        
        return LoLAPI.__VERSION
    
    @staticmethod
    def get_queue(queue_id: int) -> types.QueueDD:
        """
        Get information about the given queue.
        
        :param queue_id: queue ID
        :return: information about the queue
        :type queue_id: int
        :rtype: :class:`~types.QueueDD`
        """
        
        return LoLAPI.__QUEUES.get(queue_id, LoLAPI.__QUEUES[-1])
    
    # @staticmethod
    # def compute_queue_from_similar_description(search_queue: str):
    #     pass
    
    @staticmethod
    def get_champion_from_correct_name(name: str) -> Optional[types.ShortChampionDD]:
        """
        Get the short champion given its correct name. Useful instead of :meth:`~async_riot_api.LoLAPI.compute_champion_from_similar_name`
        if you already know the correct name.
        
        :param name: correct name of the champion, case-sensitive
        :return: short information about the champion
        :type name: str
        :rtype: Optional[:class:`~types.ShortChampionDD`]
        """
        
        return LoLAPI.__CHAMPS.get(name)
    
    @staticmethod
    def get_champion_from_id(champ_id: int) -> Optional[types.ShortChampionDD]:
        """
        Get the short champion given its ID. You can get a champ ID from many API calls.
        
        :param champ_id: integer champion ID, same as ``ShortChampionDD.int_id``
        :return: short champion
        :type champ_id: int
        :rtype: Optional[:class:`~types.ShortChampionDD`]
        """
        
        return LoLAPI.get_champion_from_correct_name(LoLAPI.__CHAMP_ID_TO_CORRECT_NAME.get(champ_id))
    
    @staticmethod
    async def get_full_champion_from_correct_name(name: str, language: str = 'en') -> types.ChampionDD:
        """
        Get the complete information about a champion given its correct name, in any available language.
        If the passed language is not present in `this list <https://ddragon.leagueoflegends.com/cdn/languages.json>`_,
        :meth:`~async_riot_api.LoLAPI.compute_language` is called.
        
        :param name: correct name of a champion, same as ``ShortChampionDD.id``
        :param language: any available language. Default 'en'
        :return: full information about a champion
        :type name: str
        :type language: str
        :rtype: :class:`~types.ChampionDD`
        """
        
        if language not in LoLAPI.__LANGUAGES:
            language = LoLAPI.compute_language(language)
        response = (await LoLAPI.__make_request(
            'GET',
            f'https://ddragon.leagueoflegends.com/cdn/{LoLAPI.__VERSION}/data/{language}/champion/{name}.json'
        ))[1]
        return types.ChampionDD(
            **(response['data'][name]),
            version = response['version']
        )
    
    @staticmethod
    def get_map_icon_url(map_id: int) -> str:
        """
        Returns the url to the image for the given map. Map ID can be found in :class:`~types.MatchDto`.
        Complete list of map IDs `here <https://static.developer.riotgames.com/docs/lol/maps.json>`_.
        
        ``IMPORTANT``: no check will be made about data existence, meaning that passing a wrong map_id will simply result
        in a broken url. No error will be raised.
        
        :param map_id: map ID
        :return: url to the given map image
        :type map_id: int
        :rtype: str
        """
        
        return f'https://ddragon.leagueoflegends.com/cdn/6.8.1/img/map/map{map_id}.png'
