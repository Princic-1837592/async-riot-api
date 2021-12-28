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
    
    :param api_key: your API token
    :type api_key: str
    :param region: region you want to use
    :type region: str
    :param routing_value: one among 'AMERICA', 'ASIA', 'ESPORTS', 'EUROPE' or 'SEA. Needed for some API calls, depends on region
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
        
        `Original method <https://developer.riotgames.com/apis#account-v1/GET_getByRiotId>`_.
        
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
        
        `Original method <https://developer.riotgames.com/apis#account-v1/GET_getActiveShard>`_.
        
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
        Get the list of masteries for a summoner.
        
        `Original method <https://developer.riotgames.com/apis#champion-mastery-v4/GET_getAllChampionMasteries>`_.
        
        :param summoner_id: summoner ID
        :type summoner_id: str
        :return: list of masteries for the given summoner
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
        :type summoner_id: str
        :param champion_id:
        :type champion_id: int
        :return: champion mastery for given summoner and champion
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
        :type summoner_id: str
        :return: mastery score of the given summoner
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
        :type summoner_id: str
        :return: list of players
        :rtype: List[:class:`~types.PlayerDto`]
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/clash/v1/players/by-summoner/{summoner_id}'),
            types.PlayerDto
        )
    
    async def get_clash_team_by_id(self, team_id: str) -> types.TeamDto:
        """
        Get a clash team by its ID.
        
        `Original method <https://developer.riotgames.com/apis#clash-v1/GET_getTeamById>`_.
        
        :param team_id:
        :type team_id: str
        :return: information about the team
        :rtype: :class:`~types.TeamDto`
        """
        
        return await LoLAPI.__create_object(
            await self.__make_api_request(f'/lol/clash/v1/teams/{team_id}'),
            types.TeamDto
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
        :type team_id: str
        :return: information about tournament
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
        :type tournament_id: int
        :return: information about the tournament
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
        :type queue: str
        :param tier: rank tier, between 'IRON' and 'CHALLENGER'
        :type tier: str
        :param division: rank division, between 'I' and 'IV' (in roman numbers)
        :type division: str
        :param page: page to select, starting from 1. Limited based on the number of entries, it's suggested to iter until results are found
        :type page: int
        :return: set of summoners for the requested queue, tier and division
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
        :type queue: str
        :return: set of challengers
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
        :type summoner_id: str
        :return: information about their ranks in every queue
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
        :type queue: str
        :param tier: rank tier, between 'IRON' and 'DIAMOND'
        :type tier: str
        :param division: rank division, between 'I' and 'IV' (in roman numbers)
        :type division: str
        :param page: page to select, starting from 1. Limited based on the number of entries, it's suggested to iter until results are found
        :type page: int
        :return: set of summoners for the requested queue, tier and division
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
        :type league_id: str
        :return: list of summoners currently in the given league
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
        :rtype: :class:`types.ShardStatus`
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
        :rtype: :class:`types.PlatformDataDto`
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
        :type puuid: str
        :return: list of match IDs sorted by recent
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
        :type match_id: str
        :return: useful information about the given LoR match
        :rtype: :class:`types.LorMatchDto`
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
        :rtype: :class:`types.LorLeaderboardDto`
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
        :rtype: :class:`types.PlatformDataDto`
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
    def get_champion_image_url_from_id(champ_id: int, skin: int = 0, type: str = 'splash') -> str:
        """
        Returns the url to the image for the given champion, skin and type.
        
        IMPORTANT: no check will be made about data existence, meaning that passing a wrong champ_id, skin or type will simply result
        in a broken url. No error will be raised.
        
        :param champ_id: champion ID, corresponding to ``ShortChampionDD.int_id``
        :type champ_id: int
        :param skin: number of the requested skin, starting from 0 for the default skin. Default 0
        :type skin: int
        :param type: type of image. Can be 'splash' or 'loading'. Default 'splash'
        :type type: str
        :return: url for the image
        :rtype: str
        """
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
    async def get_full_champion_from_correct_name(name: str, language: str = 'en') -> types.ChampionDD:
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
    def get_map_icon_url(map_id: int):
        return f'https://ddragon.leagueoflegends.com/cdn/6.8.1/img/map/map{map_id}.png'
