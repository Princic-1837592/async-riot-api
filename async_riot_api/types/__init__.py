from typing import Any, List, Optional


# SUPER-CLASS
class RiotApiResponse:
    """
    Superclass of all API responses.
    
    :param success: wether the response was successful. Useful to spot errors
    :type success: bool
    """
    
    def __init__(self, success: bool = True, **kwargs):
        self.__success = success
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_string(self, *, level: int = 0, sep = '    ', nl: str = '\n'):
        """
        Returns a prettified string representation of the object.
        
        :param level: starting level of indentation. Default: 0
        :param sep: character sequence for indentation. Default: 4 spaces
        :param nl: new line sequence. Default '\\n'
        :type level: int
        :type sep: str
        :type nl: str
        """
        
        def recursion(obj, level: int = level, sep = sep):
            if isinstance(obj, RiotApiResponse):
                return obj.to_string(level = level + 1, sep = sep)
            if isinstance(obj, list):
                return f'[{nl}{sep * (level + 2)}' + (
                    f',{nl}{sep * (level + 2)}'.join(
                        map(lambda x: recursion(x, level + 1, sep), obj)
                    )) + f'\n{sep * (level + 1)}]'
            return str(obj)
        
        to_skip = ['success', 'error', '_RiotApiResponse__success']
        return '{}({}{}{}{}{})'.format(
            type(self).__name__,
            nl,
            sep * (level + 1),
            f',{nl}{sep * (level + 1)}'.join(
                '{} = {}'.format(*item) for item in map(
                    lambda x: (x[0], recursion(x[1])),
                    filter(lambda x: x[0] not in to_skip, vars(self).items())
                )
            ),
            nl,
            sep * level,
        )
    
    def __repr__(self):
        return self.to_string()
    
    def __bool__(self):
        return self.__success


# ERROR
class RiotApiError(RiotApiResponse):
    """
    General API response error.
    
    :param message: message contained in the response. Default 'Bad Request'
    :param status_code: error code from the response. Default 400
    :type message: str
    :type status_code: int
    """
    
    def __init__(self, message: str = 'Bad Request', status_code: int = 400, **kwargs):
        super().__init__(False, **kwargs)
        self.message = message
        self.status_code = status_code


class ShortChampionDD(RiotApiResponse):
    """
    Short information about a champion
    
    :param blurb: short description
    :param id: name of the champion without non-alphabetic characters
    :param image: information about the images of a champion
    :param info: schematic information about the champion
    :param key: unique key for a champion. For some reason this is originally a string, despite representing an integer
    :param name: complete name of the champion
    :param partype: type of energy used by the champion. Usually 'Mana' but could be 'Energy' or others
    :param stats: statistics of the champion
    :param tags: tags about the champion, like 'Fighter', 'Mage'
    :param title: short title of the champion
    :param version: valid version for this object
    :type blurb: str
    :type id: str
    :type image: :class:`ChampionImageDD`
    :type info: :class:`ChampionInfoDD`
    :type key: str
    :type name: str
    :type partype: str
    :type stats: :class:`ChampionStatsDD`
    :type tags: List[str]
    :type title: str
    :type version: str
    
    Other attributes:
        int_id (``int``):
            integer representation of param ``ShortChampionDD.key``. Not present in the original data type,
            useful for some methods and, more importantly, coherent with the represented value
    """
    
    def __init__(self, blurb: str, id: str, image: dict, info: dict, key: str, name: str, partype: str, stats: dict,
                 tags: List[str], title: str, version: str, **kwargs):
        super().__init__(**kwargs)
        self.blurb = blurb
        self.id = id
        self.image: ChampionImageDD = ChampionImageDD(**image)
        self.info: ChampionInfoDD = ChampionInfoDD(**info)
        self.key = key
        self.int_id: int = int(key)
        self.name = name
        self.partype = partype
        self.stats: ChampionStatsDD = ChampionStatsDD(**stats)
        self.tags: List[str] = tags
        self.title = title
        self.version = version


class ChampionDD(ShortChampionDD):
    """
    Complete information about a champion.
    
    Look at :class:`ShortChampionDD` for the complete list of parameters.
    
    :param skins: list of skins
    :param lore: lore of the champion
    :param allytips: list of tips for summoners playing the champion
    :param enemytips: list of tipo for summoners playing against the champion
    :param spells: list of information about this champion's spells
    :param passive: information about this champion's passive ability
    :param recommended: no idea of what this is, haven't found any champion with a non-empty list of ``recommended``
    :type skins: List[:class:`ChampionSkinDD`]
    :type lore: str
    :type allytips: List[str]
    :type enemytips: List[str]
    :type spells: List[:class:`ChampionSpellDD`]
    :type passive: :class:`ChampionPassiveDD`
    :type recommended: List[unknown]
    """
    
    def __init__(self, id: str, key: str, name: str, title: str, image: dict, skins: List[dict], lore: str, blurb: str,
                 allytips: List[str], enemytips: List[str], tags: List[str], partype: str, info: dict, stats: dict,
                 spells: List[dict], passive: dict, recommended: list, version: str, **kwargs):
        super().__init__(
            blurb = blurb,
            id = id,
            image = image,
            info = info,
            key = key,
            name = name,
            partype = partype,
            stats = stats,
            tags = tags,
            title = title,
            version = version,
            **kwargs
        )
        self.skins: List[ChampionSkinDD] = list(map(lambda x: ChampionSkinDD(**x), skins))
        self.lore = lore
        self.allytips: List[str] = allytips
        self.enemytips: List[str] = enemytips
        self.spells: List[ChampionSpellDD] = list(map(lambda x: ChampionSpellDD(**x), spells))
        self.passive: ChampionPassiveDD = ChampionPassiveDD(**passive)
        self.recommended: list = recommended


class ChampionImageDD(RiotApiResponse):
    """
    Details about the champion's image.
    
    :param full: file name of the image. The complete url can be obtained from
        :meth:`~async_riot_api.LoLAPI.get_champion_image_url_from_id`
    :param sprite: don't really know what this is, some kind of image with more images inside.
        You can find more info `here <https://developer.riotgames.com/docs/lol>`_
    :param group: sub-category in which you can find the sprite of this image, more info in the same link as above
    :param x: x coordinate of the sprite in which you can find this image
    :param y: y coordinate of the sprite in which you can find this image
    :param w: width of the image in the sprite, starting from coordinates (x, y)
    :param h: height of the image in the sprite, starting from coordinates (x, y)
    :type full: str
    :type sprite: str
    :type group: str
    :type x: int
    :type y: int
    :type w: int
    :type h: int
    """
    
    def __init__(self, full: str, sprite: str, group: str, x: int, y: int, w: int, h: int, **kwargs):
        super().__init__(**kwargs)
        self.full = full
        self.sprite = sprite
        self.group = group
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class ChampionSkinDD(RiotApiResponse):
    """
    Details about the champion's skins.
    
    :param id: unique id of the skin. It is made by concatenating the champ ID and the skin number (with 3 digits).
        Example: champion "Veigar" (ID 45), skin "Final Boss" (num 8), result: "45008"
    :param num: number of the skin
    :param name: name of the skin, including the champion name (if present)
    :param chromas: if the skin has got chromas
    :type id: str
    :type num: int
    :type name: str
    :type chromas: bool
    """
    
    def __init__(self, id: str, num: int, name: str, chromas: bool, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.num = num
        self.name = name
        self.chromas = chromas


class ChampionInfoDD(RiotApiResponse):
    """
    Schematic information about the champion. You can find this information in the LoL client by going to a champion's page.
    
    :param attack: the higher this value, the higher the champion deals damage using auto attacks
    :param defense: the higher this value, the higher the champion is tanky
    :param magic: the higher this value, the higher the champion deals damage using spells
    :param difficulty: the higher this value, the more difficult is to master this champion
    :type attack: int
    :type defense: int
    :type magic: int
    :type difficulty: int
    """
    
    def __init__(self, attack: int, defense: int, magic: int, difficulty: int, **kwargs):
        super().__init__(**kwargs)
        self.attack = attack
        self.defense = defense
        self.magic = magic
        self.difficulty = difficulty


class ChampionStatsDD(RiotApiResponse):
    """
    Detailed information about a champion's base stats and how they increase when leveling up.
    Here i list their meanings and their unit of measurement where:
        - ``u`` stands for "unit"
        - ``l`` stands for "level"
        - ``s`` stands for "second"
    
    :param hp: base health points (``u``)
    :param hpperlevel: extra HP per level (``u / l``)
    :param mp: base mana points (``u``)
    :param mpperlevel: extra mana points per level (``u / l``)
    :param movespeed: base movement speed (``u / s``)
    :param armor: base armor (``u``)
    :param armorperlevel: extra armor per level (``u / l``)
    :param spellblock: base magic resistance (``u``)
    :param spellblockperlevel: extra magic resistance per level (``u / l``)
    :param attackrange: base attack range (``u``)
    :param hpregen: base HP regeneration (``u / 5s``)
    :param hpregenperlevel: extra HP regeneration per level (``u / 5s / l``)
    :param mpregen: base mana regeneration (``u / 5s``)
    :param mpregenperlevel: extra mana regeneration per level (``u / 5s / l``)
    :param crit: base critical chance (``u``)
    :param critperlevel: extra critical chance per level (``u / l``)
    :param attackdamage: base attack damage (``u``)
    :param attackdamageperlevel: extra attack damage per level (``u / l``)
    :param attackspeedperlevel: extra attack speed per level (``u / s / l``)
    :param attackspeed: base attack speed (``u / s``)
    :type hp: int
    :type hpperlevel: int
    :type mp: int
    :type mpperlevel: int
    :type movespeed: int
    :type armor: int
    :type armorperlevel: float
    :type spellblock: int
    :type spellblockperlevel: float
    :type attackrange: int
    :type hpregen: int
    :type hpregenperlevel: int
    :type mpregen: int
    :type mpregenperlevel: int
    :type crit: int
    :type critperlevel: int
    :type attackdamage: int
    :type attackdamageperlevel: int
    :type attackspeedperlevel: float
    :type attackspeed: float
    """
    
    def __init__(self, hp: int, hpperlevel: int, mp: int, mpperlevel: int, movespeed: int, armor: int,
                 armorperlevel: float, spellblock: int, spellblockperlevel: float, attackrange: int, hpregen: int,
                 hpregenperlevel: int, mpregen: int, mpregenperlevel: int, crit: int, critperlevel: int,
                 attackdamage: int, attackdamageperlevel: int, attackspeedperlevel: float, attackspeed: float,
                 **kwargs):
        super().__init__(**kwargs)
        self.hp = hp
        self.hpperlevel = hpperlevel
        self.mp = mp
        self.mpperlevel = mpperlevel
        self.movespeed = movespeed
        self.armor = armor
        self.armorperlevel = armorperlevel
        self.spellblock = spellblock
        self.spellblockperlevel = spellblockperlevel
        self.attackrange = attackrange
        self.hpregen = hpregen
        self.hpregenperlevel = hpregenperlevel
        self.mpregen = mpregen
        self.mpregenperlevel = mpregenperlevel
        self.crit = crit
        self.critperlevel = critperlevel
        self.attackdamage = attackdamage
        self.attackdamageperlevel = attackdamageperlevel
        self.attackspeedperlevel = attackspeedperlevel
        self.attackspeed = attackspeed


class ChampionSpellDD(RiotApiResponse):
    """
    Specific information about a champion spell (skill). Complete documentation about string placeholders and parsing is
    `here <https://developer.riotgames.com/docs/lol>`_.
    
    :param id: spell's ID, including champion name and spell name
    :param name: spell's name
    :param description: spell's description
    :param tooltip: similar to ``description``, but contains placeholders to build a string including data about damage per level, AP/AD scaling ecc.
        Can be parsed to make the string look like the one in game
    :param maxrank: maximum rank for this ability
    :param cooldown: data about placeholders for cooldown
    :param cooldownBurn: like ``cooldown``, but as string
    :param cost: data about placeholders for cost
    :param costBurn: like ``cost``, but as string
    :param datavalues: no documentation found. No champion found with a non-empty dict of ``datavalues``
    :param effect: like ``cost``, but when the spell costs health. The first element is always None for design reasons
    :param effectBurn: like ``effect``, but as string
    :param vars: no documentation found. No champion found with a non-empty list of ``vars``
    :param costType: type of resources spent for using the ability
    :param maxammo: in case the spell has ammos, like traps. '-1' if no ammos. For some reason this integer is represented as a string
    :param range: data about placeholders for range
    :param rangeBurn: like ``range``, but as string
    :param image: details about the spell's image
    :param leveltip: data about placeholders for levels
    :param resource: placeholder for cost
    :type id: str
    :type name: str
    :type description: str
    :type tooltip: str
    :type leveltip: :class:`ChampionSpellLeveltipDD`
    :type maxrank: int
    :type cooldown: List[int]
    :type cooldownBurn: str
    :type cost: List[int]
    :type costBurn: str
    :type datavalues: :class:`ChampionSpellDatavaluesDD`
    :type effect: List[Optional[List[int]]]
    :type effectBurn: List[Optional[str]]
    :type vars: List[unknown]
    :type costType: str
    :type maxammo: str
    :type range: List[int]
    :type rangeBurn: str
    :type image: :class:`ChampionSpellImageDD`
    :type resource: Optional[str]
    """
    
    def __init__(self, id: str, name: str, description: str, tooltip: str, maxrank: int,
                 cooldown: List[int], cooldownBurn: str, cost: List[int], costBurn: str, datavalues: dict,
                 effect: List[Optional[List[int]]], effectBurn: List[Optional[str]], vars: List[Any], costType: str,
                 maxammo: str,
                 range: List[int], rangeBurn: str, image: dict, leveltip: Optional[dict] = None,
                 resource: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.name = name
        self.description = description
        self.tooltip = tooltip
        self.maxrank = maxrank
        self.cooldown: List[int] = cooldown
        self.cooldownBurn = cooldownBurn
        self.cost: List[int] = cost
        self.costBurn = costBurn
        self.datavalues: ChampionSpellDatavaluesDD = ChampionSpellDatavaluesDD(**datavalues)
        self.effect = effect
        self.effectBurn = effectBurn
        self.vars: List[Any] = vars
        self.costType = costType
        self.maxammo = maxammo
        self.range: List[int] = range
        self.rangeBurn = rangeBurn
        self.image: ChampionSpellImageDD = ChampionSpellImageDD(**image)
        self.leveltip: ChampionSpellLeveltipDD = None if leveltip is None else ChampionSpellLeveltipDD(**leveltip)
        self.resource = resource


class ChampionSpellLeveltipDD(RiotApiResponse):
    def __init__(self, label: List[str], effect: List[str], **kwargs):
        super().__init__(**kwargs)
        self.label: List[str] = label
        self.effect: List[str] = effect


class ChampionSpellDatavaluesDD(RiotApiResponse):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ChampionSpellImageDD(RiotApiResponse):
    def __init__(self, full: str, sprite: str, group: str, x: int, y: int, w: int, h: int, **kwargs):
        super().__init__(**kwargs)
        self.full = full
        self.sprite = sprite
        self.group = group
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class ChampionPassiveDD(RiotApiResponse):
    def __init__(self, name: str, description: str, image: dict, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.image: ChampionPassiveImageDD = ChampionPassiveImageDD(**image)


class ChampionPassiveImageDD(RiotApiResponse):
    def __init__(self, full: str, sprite: str, group: str, x: int, y: int, w: int, h: int, **kwargs):
        super().__init__(**kwargs)
        self.full = full
        self.sprite = sprite
        self.group = group
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class QueueDD(RiotApiResponse):
    """
    Representation of a queue. Not actually returned by any API call, but still usefu sometimes.
    
    :param queueId: queue ID
    :param map: map name
    :param description: description of the queue
    :param notes: notes about the queue, like 'deprecated since version x'
    :type queueId: int
    :type map: str
    :type description: str
    :type notes: str
    """
    
    def __init__(self, queueId: int, map: str, description: str, notes: str, **kwargs):
        super().__init__(**kwargs)
        self.queueId = queueId
        self.map = map
        self.description = description
        self.notes = notes


# ACCOUNT-V1
class AccountDto(RiotApiResponse):
    """
    Basic information about a Riot Games account.
    
    :param puuid: puuid of the account. Useful for many API methods
    :param gameName: in-game name of the account
    :param tagLine: tag line of the account
    :type puuid: str
    :type gameName: str
    :type tagLine: str
    """
    
    def __init__(self, puuid: str, gameName: str, tagLine: str, **kwargs):
        super().__init__(**kwargs)
        self.puuid = puuid
        self.gameName = gameName
        self.tagLine = tagLine


class ActiveShardDto(RiotApiResponse):
    """
    No idea about what this is. Probably the server in which the summoner plays.
    
    :param puuid: puuid
    :param game: game. Can be 'val' or 'lor'
    :param activeShard: probably the server in which the summoner plays
    :type puuid: str
    :type game: str
    :type activeShard: str
    """
    
    def __init__(self, puuid: str, game: str, activeShard: str, **kwargs):
        super().__init__(**kwargs)
        self.puuid = puuid
        self.game = game
        self.activeShard = activeShard


# CHAMPION-MASTERY-V4
class ChampionMasteryDto(RiotApiResponse):
    """
    Information about a summoner's mastery levels, tokens and chests.
    
    :param championPointsUntilNextLevel: points needed for the mastery to upgrade to the next level
    :param chestGranted: if the player already got the weekly chest on the champion
    :param championId: champion ID
    :param lastPlayTime: laste time the player played the champion
    :param championLevel: mastery level for the champion. Min 1, max 7
    :param summonerId: summoner ID
    :param championPoints: mastery points for the champion
    :param championPointsSinceLastLevel: points earned since last mastery level
    :param tokensEarned: tokens earned to upgrade the mastery level to level 6 (0-2) or 7 (0-3)
    :type championPointsUntilNextLevel: int
    :type chestGranted: bool
    :type championId: int
    :type lastPlayTime: int
    :type championLevel: int
    :type summonerId: str
    :type championPoints: int
    :type championPointsSinceLastLevel: int
    :type tokensEarned: int
    """
    
    def __init__(self, championPointsUntilNextLevel: int, chestGranted: bool, championId: int, lastPlayTime: int,
                 championLevel: int, summonerId: str, championPoints: int, championPointsSinceLastLevel: int,
                 tokensEarned: int, **kwargs):
        super().__init__(**kwargs)
        self.championPointsUntilNextLevel = championPointsUntilNextLevel
        self.chestGranted = chestGranted
        self.championId = championId
        self.lastPlayTime = lastPlayTime
        self.championLevel = championLevel
        self.summonerId = summonerId
        self.championPoints = championPoints
        self.championPointsSinceLastLevel = championPointsSinceLastLevel
        self.tokensEarned = tokensEarned


# CHAMPION-V3
class ChampionInfo(RiotApiResponse):
    """
    Information about the current champion rotation and the new players' champion rotation.
    
    :param maxNewPlayerLevel: max level for a player to have the beginner rotation available
    :param freeChampionIdsForNewPlayers: list of champion IDs free-to-play for beginners
    :param freeChampionIds: list of champion IDs free-to-play for non-beginner players
    :type maxNewPlayerLevel: int
    :type freeChampionIdsForNewPlayers: List[int]
    :type freeChampionIds: List[int[
    """
    
    def __init__(self, maxNewPlayerLevel: int, freeChampionIdsForNewPlayers: List[int], freeChampionIds: List[int],
                 **kwargs):
        super().__init__(**kwargs)
        self.maxNewPlayerLevel = maxNewPlayerLevel
        self.freeChampionIdsForNewPlayers = freeChampionIdsForNewPlayers
        self.freeChampionIds = freeChampionIds


# CLASH-V1
class PlayerDto(RiotApiResponse):
    """
    Data about a player in a clash.
    
    :param summonerId: summoner ID
    :param teamId: team ID
    :param position: position selected by the summoner
    :param role: role selected by the summoner
    :type summonerId: str
    :type teamId: str
    :type position: str
    :type role: str
    """
    
    def __init__(self, summonerId: str, teamId: str, position: str, role: str, **kwargs):
        super().__init__(**kwargs)
        self.summonerId = summonerId
        self.teamId = teamId
        self.position = position
        self.role = role


class TournamentDto(RiotApiResponse):
    """
    Information about a tournament.
    
    :param id: tournament ID
    :param themeId: no idea, not originally documented
    :param nameKey: no idea, not originally documented
    :param nameKeySecondary: no idea, not originally documented
    :param schedule: schedule for this tournament
    :type id: int
    :type themeId: int
    :type nameKey: str
    :type nameKeySecondary: str
    :type schedule: :class:`TournamentPhaseDto`
    """
    
    def __init__(self, id: int, themeId: int, nameKey: str, nameKeySecondary: str, schedule: List[dict], **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.themeId = themeId
        self.nameKey = nameKey
        self.nameKeySecondary = nameKeySecondary
        self.schedule: List[TournamentPhaseDto] = list(map(lambda x: TournamentPhaseDto(**x), schedule))


class TournamentPhaseDto(RiotApiResponse):
    """
    Schedule information for a tournament.
    
    :param id: ID
    :param registrationTime: timestamp in ms
    :param startTime: timestamp in ms
    :param cancelled: wether the tournament is cancelled
    :type id: int
    :type registrationTime: int
    :type startTime: int
    :type cancelled: bool
    """
    
    def __init__(self, id: int, registrationTime: int, startTime: int, cancelled: bool, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.registrationTime = registrationTime
        self.startTime = startTime
        self.cancelled = cancelled


# LEAGUE-V4
class LeagueListDTO(RiotApiResponse):
    """
    List of information about leagues for summoners in the same queue.
    
    :param tier: rank tier, like 'CHALLENGER' or 'MASTER'
    :param leagueId: league ID
    :param queue: queue type, like 'RANKED_SOLO_5x5'
    :param name: list name
    :param entries: entries for this list
    :type tier: str
    :type leagueId: str
    :type queue: str
    :type name: str
    :type entries: List[:class:`LeagueItemDTO`]
    """
    
    def __init__(self, tier: str, leagueId: str, queue: str, name: str, entries: List[dict], **kwargs):
        super().__init__(**kwargs)
        self.tier = tier
        self.leagueId = leagueId
        self.queue = queue
        self.name = name
        self.entries: List[LeagueItemDTO] = list(map(lambda x: LeagueItemDTO(**x), entries))


class LeagueItemDTO(RiotApiResponse):
    """
    Simplified information about a summoner's rank in a queue, returned by methods for apex tiers.
    Some information are missing since they are included in the higher level object ``LeagueListDTO`` containing this object.
    
    :param summonerId: summoner ID
    :param summonerName: summoner name
    :param leaguePoints: aka LP
    :param rank: rank of the summoner, between 'I' and 'IV' (in roman numbers)
    :param wins: wins for this season
    :param losses: losses for this season
    :param veteran: wether the summoner is a veteran in this rank
    :param inactive: wether the summoner is inactive
    :param freshBlood: wether the summoner is a new entry in this rank
    :param hotStreak: wether the summoner is on a hot streak (winning streak)
    :param miniSeries: information about a summoner miniseries, if they are about to get promoted from a tier to the next
    :type summonerId: str
    :type summonerName: str
    :type leaguePoints: int
    :type rank: str
    :type wins: int
    :type losses: int
    :type veteran: bool
    :type inactive: bool
    :type freshBlood: bool
    :type hotStreak: bool
    :type miniSeries: Optional[:class:`MiniSeriesDTO`]
    """
    
    def __init__(self, summonerId: str, summonerName: str, leaguePoints: int, rank: str, wins: int, losses: int,
                 veteran: bool, inactive: bool, freshBlood: bool, hotStreak: bool, miniSeries: Optional[dict] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.summonerId = summonerId
        self.summonerName = summonerName
        self.leaguePoints = leaguePoints
        self.rank = rank
        self.wins = wins
        self.losses = losses
        self.veteran = veteran
        self.inactive = inactive
        self.freshBlood = freshBlood
        self.hotStreak = hotStreak
        self.miniSeries: Optional[MiniSeriesDTO] = None if miniSeries is None else MiniSeriesDTO(**miniSeries)


class LeagueEntryDTO(LeagueItemDTO):
    """
    Complete information about summoner's league.

    Look at :class:`LeagueItemDTO` for the complete list of parameters.
    
    :param queueType: queue for this entry, like 'RANKED_SOLO_5x5'
    :param leagueId: league ID
    :param tier: tier for this entry, like 'SILVER' or 'DIAMOND'
    :type queueType: str
    :type leagueId: Optional[str]
    :type tier: Optional[str]
    
    Other attributes:
        short (``Optional[str]``):
            short representation of rank and tier. For example 'DIAMOND III' becomes 'D3'.
            Exception is made for 'GRANDMASTER x' which becomes 'GMx' due to the ambuguity between 'GOLD' and 'GRANDMASTER'
    """
    
    def __init__(self, summonerId: str, summonerName: str, queueType: str, leaguePoints: int, wins: int, losses: int,
                 hotStreak: bool, veteran: bool, freshBlood: bool, inactive: bool, miniSeries: Optional[dict] = None,
                 leagueId: Optional[str] = None, tier: Optional[str] = None, rank: Optional[str] = None, **kwargs):
        super().__init__(
            summonerId = summonerId,
            summonerName = summonerName,
            leaguePoints = leaguePoints,
            rank = rank,
            wins = wins,
            losses = losses,
            veteran = veteran,
            inactive = inactive,
            freshBlood = freshBlood,
            hotStreak = hotStreak,
            miniSeries = miniSeries,
            **kwargs
        )
        self.leagueId = leagueId
        self.queueType = queueType
        self.tier = tier
        self.short: Optional[str] = LeagueEntryDTO.__get_short(self.tier, self.rank)
    
    @staticmethod
    def __get_short(tier: str, rank: str) -> Optional[str]:
        if not (tier and rank):
            return None
        return f"{('GM' if tier.startswith('GR') else tier[0])}{'4' if rank.lower() == 'iv' else len(rank)}"


class MiniSeriesDTO(RiotApiResponse):
    """
    Information about a summoner's miniseries, if they are about to get promoted to the next tier.
    Miniseries consist in 5 matches in which you have to win 3 times to get promoted.
    Before season 11, miniseries were also required when passing from a rank to another,
    with 3 matches instead of 5 and 2 victories instead of 3.
    
    :param losses: losses in this miniseries
    :param progress: string representing wins and losses. for example 'WWLNN' means two wins, one loss and two matches remained
    :param target: number of wins to reach
    :param wins: wins in this miniseries
    :type losses: int
    :type progress: str
    :type target: int
    :type wins: int
    """
    
    def __init__(self, losses: int, progress: str, target: int, wins: int, **kwargs):
        super().__init__(**kwargs)
        self.losses = losses
        self.progress = progress
        self.target = target
        self.wins = wins


# LOL-STATUS-V3
class ShardStatus(RiotApiResponse):
    def __init__(self, name: str, slug: str, locales: List[str], hostname: str, region_tag: str, services: List[dict],
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.slug = slug
        self.locales = locales
        self.hostname = hostname
        self.region_tag = region_tag
        self.services: List[Service] = list(map(lambda x: Service(**x), services))


class Service(RiotApiResponse):
    def __init__(self, name: str, slug: str, status: str, incidents: List[dict], **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.slug = slug
        self.status = status
        self.incidents: List[Incident] = list(map(lambda x: Incident(**x), incidents))


class Incident(RiotApiResponse):
    def __init__(self, id: int, active: bool, created_at: str, updates: List[dict], **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.active = active
        self.created_at = created_at
        self.updates: List[Message] = list(map(lambda x: Message(**x), updates))


class Message(RiotApiResponse):
    def __init__(self, id: str, author: str, heading: str, content: str, severity: str, created_at: str,
                 updated_at: str, translations: List[dict], **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.author = author
        self.heading = heading
        self.content = content
        self.severity = severity
        self.created_at = created_at
        self.updated_at = updated_at
        self.translations: List[Translation] = list(map(lambda x: Translation(**x), translations))


class Translation(RiotApiResponse):
    def __init__(self, locale: str, heading: str, content: str, **kwargs):
        super().__init__(**kwargs)
        self.locale = locale
        self.heading = heading
        self.content = content


# LOL-STATUS-V4
class PlatformDataDto(RiotApiResponse):
    def __init__(self, id: str, name: str, locales: List[str], maintenances: List[dict], incidents: List[dict],
                 **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.name = name
        self.locales = locales
        self.maintenances: List[StatusDto] = list(map(lambda x: StatusDto(**x), maintenances))
        self.incidents: List[StatusDto] = list(map(lambda x: StatusDto(**x), incidents))


class StatusDto(RiotApiResponse):
    def __init__(self, id: int, maintenance_status: str, incident_severity: Optional[str], titles: List[dict],
                 updates: List[dict], created_at: str, archive_at: str, updated_at: Optional[str],
                 platforms: List[str], **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.maintenance_status = maintenance_status
        self.incident_severity = incident_severity
        self.titles: List[ContentDto] = list(map(lambda x: ContentDto(**x), titles))
        self.updates: List[UpdateDto] = list(map(lambda x: UpdateDto(**x), updates))
        self.created_at = created_at
        self.archive_at = archive_at
        self.updated_at = updated_at
        self.platforms = platforms


class ContentDto(RiotApiResponse):
    def __init__(self, locale: str, content: str, **kwargs):
        super().__init__(**kwargs)
        self.locale = locale
        self.content = content


class UpdateDto(RiotApiResponse):
    def __init__(self, id: int, author: str, publish: bool, publish_locations: List[str], translations: List[dict],
                 created_at: str, updated_at: str, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.author = author
        self.publish = publish
        self.publish_locations = publish_locations
        self.translations: List[ContentDto] = list(map(lambda x: ContentDto(**x), translations))
        self.created_at = created_at
        self.updated_at = updated_at


# LOR-MATCH-V1
class LorMatchDto(RiotApiResponse):
    """
    Base object containing inforamtion about a LoR match.
    
    :param metadata: to access the ordered list of participants
    :param info: more detailed infor about players
    :type metadata: :class:`LorMetadataDto`
    :type info: :class:`LorInfoDto`
    """
    
    def __init__(self, metadata: dict, info: dict, **kwargs):
        super().__init__(**kwargs)
        self.metadata: LorMetadataDto = LorMetadataDto(**metadata)
        self.info: LorInfoDto = LorInfoDto(**info)


class LorMetadataDto(RiotApiResponse):
    """
    Metadata about the match.
    
    :param data_version: version of the game
    :param match_id: match ID
    :param participants: ordered list of participants, represented by their puuid
    :type data_version: str
    :type match_id: str
    :type participants: List[str]
    """
    
    def __init__(self, data_version: str, match_id: str, participants: List[str], **kwargs):
        super().__init__(**kwargs)
        self.data_version = data_version
        self.match_id = match_id
        self.participants: List[str] = participants


class LorInfoDto(RiotApiResponse):
    """
    Detailed information about a LoR match. Contains information about mode, duration and players.
    
    :param game_mode: game mode
    :param game_type: game type
    :param game_start_time_utc: game start time utc
    :param game_version: game version
    :param players: list of detailed information about the players involved in the match, in the same order as :class:`LorMetadataDto`
    :param total_turn_count: total turn count
    :type game_mode: str
    :type game_type: str
    :type game_start_time_utc: str
    :type game_version: str
    :type players: List[:class:`LorPlayerDto`]
    :type total_turn_count: int
    """
    
    def __init__(self, game_mode: str, game_type: str, game_start_time_utc: str, game_version: str, players: List[dict],
                 total_turn_count: int, **kwargs):
        super().__init__(**kwargs)
        self.game_mode = game_mode
        self.game_type = game_type
        self.game_start_time_utc = game_start_time_utc
        self.game_version = game_version
        self.players: List[LorPlayerDto] = list(map(lambda x: LorPlayerDto(**x), players))
        self.total_turn_count = total_turn_count


class LorPlayerDto(RiotApiResponse):
    """
    Detailed information about a player in a LoR match.
    
    :param puuid: puuid
    :param deck_id: deck ID
    :param deck_code: deck code
    :param factions: factions persent in the deck
    :param game_outcome: result of the game
    :param order_of_play: order if play in the game
    :type puuid: str
    :type deck_id: str
    :type deck_code: str
    :type factions: List[str]
    :type game_outcome: str
    :type order_of_play: int
    """
    
    def __init__(self, puuid: str, deck_id: str, deck_code: str, factions: List[str], game_outcome: str,
                 order_of_play: int, **kwargs):
        super().__init__(**kwargs)
        self.puuid = puuid
        self.deck_id = deck_id
        self.deck_code = deck_code
        self.factions: List[str] = factions
        self.game_outcome = game_outcome
        self.order_of_play = order_of_play


# LOR-RANKED-V1
class LorLeaderboardDto(RiotApiResponse):
    """
    List of players in LoR Master tier.
    :param players: list of players
    :type players: List[:class:`LorLeaderboardPlayerDto`]
    """
    
    def __init__(self, players: List[dict], **kwargs):
        super().__init__(**kwargs)
        self.players: List[LorLeaderboardPlayerDto] = list(map(lambda x: LorLeaderboardPlayerDto(**x), players))


class LorLeaderboardPlayerDto(RiotApiResponse):
    """
    Information about a player in LoR Master tier.
    
    :param name: summoner's name
    :param rank: summoner's rank
    :param lp: summoner's LP
    :type name: str
    :type rank: int
    :type lp: int
    """
    
    def __init__(self, name: str, rank: int, lp: int, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.rank = rank
        self.lp = lp


# MATCH-V5
class MatchDto(RiotApiResponse):
    def __init__(self, metadata: dict, info: dict, **kwargs):
        super().__init__(**kwargs)
        self.metadata: MetadataDto = MetadataDto(**metadata)
        self.info: InfoDto = InfoDto(**info)


class MetadataDto(RiotApiResponse):
    def __init__(self, dataVersion: str, matchId: str, participants: List[str], **kwargs):
        super().__init__(**kwargs)
        self.dataVersion = dataVersion
        self.matchId = matchId
        self.participants = participants


class InfoDto(RiotApiResponse):
    def __init__(self, gameCreation: int, gameDuration: int, gameId: int, gameMode: str, gameName: str,
                 gameStartTimestamp: int, gameType: str, gameVersion: str, mapId: int, participants: List[str],
                 platformId: str, queueId: int, teams: List[dict], tournamentCode: Optional[str] = None,
                 gameEndTimestamp: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.gameCreation = gameCreation
        self.gameDuration = gameDuration
        self.gameId = gameId
        self.gameMode = gameMode
        self.gameName = gameName
        self.gameStartTimestamp = gameStartTimestamp
        self.gameEndTimestamp = gameEndTimestamp or gameStartTimestamp + gameDuration
        self.gameType = gameType
        self.gameVersion = gameVersion
        self.mapId = mapId
        self.participants: List[ParticipantDto] = list(map(lambda x: ParticipantDto(**x), participants))
        self.platformId = platformId
        self.queueId = queueId
        self.teams: List[TeamDto] = list(map(lambda x: TeamDto(**x), teams))
        self.tournamentCode = tournamentCode
        self.gameDurationSeconds: int = gameDuration > 10000 and gameDuration // 1000 or gameDuration


class ParticipantDto(RiotApiResponse):
    def __init__(self, assists: int, baronKills: int, bountyLevel: int, champExperience: int, champLevel: int,
                 championId: int, championName: str, championTransform: int, consumablesPurchased: int,
                 damageDealtToBuildings: int, damageDealtToObjectives: int, damageDealtToTurrets: int,
                 damageSelfMitigated: int, deaths: int, detectorWardsPlaced: int, doubleKills: int, dragonKills: int,
                 firstBloodAssist: bool, firstBloodKill: bool, firstTowerAssist: bool, firstTowerKill: bool,
                 gameEndedInEarlySurrender: bool, gameEndedInSurrender: bool, goldEarned: int, goldSpent: int,
                 individualPosition: str, inhibitorKills: int, inhibitorsLost: int, item0: int,
                 item1: int, item2: int, item3: int, item4: int, item5: int, item6: int, itemsPurchased: int,
                 killingSprees: int, kills: int, lane: str, largestCriticalStrike: int, largestKillingSpree: int,
                 largestMultiKill: int, longestTimeSpentLiving: int, magicDamageDealt: int,
                 magicDamageDealtToChampions: int, magicDamageTaken: int, neutralMinionsKilled: int, nexusKills: int,
                 nexusLost: int, objectivesStolen: int, objectivesStolenAssists: int,
                 participantId: int, pentaKills: int, perks: dict, physicalDamageDealt: int,
                 physicalDamageDealtToChampions: int, physicalDamageTaken: int, profileIcon: int, puuid: str,
                 quadraKills: int, riotIdName: str, riotIdTagline: str, role: str, sightWardsBoughtInGame: int,
                 spell1Casts: int, spell2Casts: int, spell3Casts: int, spell4Casts: int, summoner1Casts: int,
                 summoner1Id: int, summoner2Casts: int, summoner2Id: int, summonerId: str, summonerLevel: int,
                 summonerName: str, teamEarlySurrendered: bool, teamId: int, teamPosition: str, timeCCingOthers: int,
                 timePlayed: int, totalDamageDealt: int, totalDamageDealtToChampions: int,
                 totalDamageShieldedOnTeammates: int, totalDamageTaken: int, totalHeal: int, totalHealsOnTeammates: int,
                 totalMinionsKilled: int, totalTimeCCDealt: int, totalTimeSpentDead: int, totalUnitsHealed: int,
                 tripleKills: int, trueDamageDealt: int, trueDamageDealtToChampions: int, trueDamageTaken: int,
                 turretKills: int, turretsLost: int, unrealKills: int, visionScore: int,
                 visionWardsBoughtInGame: int, wardsKilled: int, wardsPlaced: int, win: bool,
                 inhibitorTakedowns: int = 0, nexusTakedowns: int = 0, turretTakedowns: int = 0, **kwargs):
        """
        
        :param assists: 
        :param baronKills: 
        :param bountyLevel: 
        :param champExperience: 
        :param champLevel: 
        :param championId: 
        :param championName: 
        :param championTransform: 
        :param consumablesPurchased: 
        :param damageDealtToBuildings: 
        :param damageDealtToObjectives: 
        :param damageDealtToTurrets: 
        :param damageSelfMitigated: 
        :param deaths: 
        :param detectorWardsPlaced: 
        :param doubleKills: 
        :param dragonKills: 
        :param firstBloodAssist: 
        :param firstBloodKill: 
        :param firstTowerAssist: 
        :param firstTowerKill: 
        :param gameEndedInEarlySurrender: 
        :param gameEndedInSurrender: 
        :param goldEarned: 
        :param goldSpent: 
        :param individualPosition: 
        :param inhibitorKills: 
        :param inhibitorsLost: 
        :param item0: 
        :param item1: 
        :param item2: 
        :param item3: 
        :param item4: 
        :param item5: 
        :param item6: 
        :param itemsPurchased: 
        :param killingSprees: 
        :param kills: 
        :param lane: 
        :param largestCriticalStrike: 
        :param largestKillingSpree: 
        :param largestMultiKill: 
        :param longestTimeSpentLiving: 
        :param magicDamageDealt: 
        :param magicDamageDealtToChampions: 
        :param magicDamageTaken: 
        :param neutralMinionsKilled: 
        :param nexusKills: 
        :param nexusLost: 
        :param objectivesStolen: 
        :param objectivesStolenAssists: 
        :param participantId: 
        :param pentaKills: 
        :param perks: 
        :param physicalDamageDealt: 
        :param physicalDamageDealtToChampions: 
        :param physicalDamageTaken: 
        :param profileIcon: 
        :param puuid: 
        :param quadraKills: 
        :param riotIdName: 
        :param riotIdTagline: 
        :param role: 
        :param sightWardsBoughtInGame: 
        :param spell1Casts: 
        :param spell2Casts: 
        :param spell3Casts: 
        :param spell4Casts: 
        :param summoner1Casts: 
        :param summoner1Id: 
        :param summoner2Casts: 
        :param summoner2Id: 
        :param summonerId: 
        :param summonerLevel: 
        :param summonerName: 
        :param teamEarlySurrendered: 
        :param teamId: 
        :param teamPosition: 
        :param timeCCingOthers: 
        :param timePlayed: 
        :param totalDamageDealt: 
        :param totalDamageDealtToChampions: 
        :param totalDamageShieldedOnTeammates: 
        :param totalDamageTaken: 
        :param totalHeal: 
        :param totalHealsOnTeammates: 
        :param totalMinionsKilled: 
        :param totalTimeCCDealt: 
        :param totalTimeSpentDead: 
        :param totalUnitsHealed: 
        :param tripleKills: 
        :param trueDamageDealt: 
        :param trueDamageDealtToChampions: 
        :param trueDamageTaken: 
        :param turretKills: 
        :param turretsLost: 
        :param unrealKills: 
        :param visionScore: 
        :param visionWardsBoughtInGame: 
        :param wardsKilled: 
        :param wardsPlaced: 
        :param win: 
        :param inhibitorTakedowns: 
        :param nexusTakedowns: 
        :param turretTakedowns: 
        :type assists: 
        :type baronKills: 
        :type bountyLevel: 
        :type champExperience: 
        :type champLevel: 
        :type championId: 
        :type championName: 
        :type championTransform: 
        :type consumablesPurchased: 
        :type damageDealtToBuildings: 
        :type damageDealtToObjectives: 
        :type damageDealtToTurrets: 
        :type damageSelfMitigated: 
        :type deaths: 
        :type detectorWardsPlaced: 
        :type doubleKills: 
        :type dragonKills: 
        :type firstBloodAssist: 
        :type firstBloodKill: 
        :type firstTowerAssist: 
        :type firstTowerKill: 
        :type gameEndedInEarlySurrender: 
        :type gameEndedInSurrender: 
        :type goldEarned: 
        :type goldSpent: 
        :type individualPosition: 
        :type inhibitorKills: 
        :type inhibitorsLost: 
        :type item0: 
        :type item1: 
        :type item2: 
        :type item3: 
        :type item4: 
        :type item5: 
        :type item6: 
        :type itemsPurchased: 
        :type killingSprees: 
        :type kills: 
        :type lane: 
        :type largestCriticalStrike: 
        :type largestKillingSpree: 
        :type largestMultiKill: 
        :type longestTimeSpentLiving: 
        :type magicDamageDealt: 
        :type magicDamageDealtToChampions: 
        :type magicDamageTaken: 
        :type neutralMinionsKilled: 
        :type nexusKills: 
        :type nexusLost: 
        :type objectivesStolen: 
        :type objectivesStolenAssists: 
        :type participantId: 
        :type pentaKills: 
        :type perks: 
        :type physicalDamageDealt: 
        :type physicalDamageDealtToChampions: 
        :type physicalDamageTaken: 
        :type profileIcon: 
        :type puuid: 
        :type quadraKills: 
        :type riotIdName: 
        :type riotIdTagline: 
        :type role: 
        :type sightWardsBoughtInGame: 
        :type spell1Casts: 
        :type spell2Casts: 
        :type spell3Casts: 
        :type spell4Casts: 
        :type summoner1Casts: 
        :type summoner1Id: 
        :type summoner2Casts: 
        :type summoner2Id: 
        :type summonerId: 
        :type summonerLevel: 
        :type summonerName: 
        :type teamEarlySurrendered: 
        :type teamId: 
        :type teamPosition: 
        :type timeCCingOthers: 
        :type timePlayed: 
        :type totalDamageDealt: 
        :type totalDamageDealtToChampions: 
        :type totalDamageShieldedOnTeammates: 
        :type totalDamageTaken: 
        :type totalHeal: 
        :type totalHealsOnTeammates: 
        :type totalMinionsKilled: 
        :type totalTimeCCDealt: 
        :type totalTimeSpentDead: 
        :type totalUnitsHealed: 
        :type tripleKills: 
        :type trueDamageDealt: 
        :type trueDamageDealtToChampions: 
        :type trueDamageTaken: 
        :type turretKills: 
        :type turretsLost: 
        :type unrealKills: 
        :type visionScore: 
        :type visionWardsBoughtInGame: 
        :type wardsKilled: 
        :type wardsPlaced: 
        :type win: 
        :type inhibitorTakedowns: 
        :type nexusTakedowns: 
        :type turretTakedowns: 
        """
        super().__init__(**kwargs)
        self.assists = assists
        self.baronKills = baronKills
        self.bountyLevel = bountyLevel
        self.champExperience = champExperience
        self.champLevel = champLevel
        self.championId = championId
        self.championName = championName
        self.championTransform = championTransform
        self.consumablesPurchased = consumablesPurchased
        self.damageDealtToBuildings = damageDealtToBuildings
        self.damageDealtToObjectives = damageDealtToObjectives
        self.damageDealtToTurrets = damageDealtToTurrets
        self.damageSelfMitigated = damageSelfMitigated
        self.deaths = deaths
        self.detectorWardsPlaced = detectorWardsPlaced
        self.doubleKills = doubleKills
        self.dragonKills = dragonKills
        self.firstBloodAssist = firstBloodAssist
        self.firstBloodKill = firstBloodKill
        self.firstTowerAssist = firstTowerAssist
        self.firstTowerKill = firstTowerKill
        self.gameEndedInEarlySurrender = gameEndedInEarlySurrender
        self.gameEndedInSurrender = gameEndedInSurrender
        self.goldEarned = goldEarned
        self.goldSpent = goldSpent
        self.individualPosition = individualPosition
        self.inhibitorKills = inhibitorKills
        self.inhibitorTakedowns = inhibitorTakedowns
        self.inhibitorsLost = inhibitorsLost
        self.item0 = item0
        self.item1 = item1
        self.item2 = item2
        self.item3 = item3
        self.item4 = item4
        self.item5 = item5
        self.item6 = item6
        self.itemsPurchased = itemsPurchased
        self.killingSprees = killingSprees
        self.kills = kills
        self.lane = lane
        self.largestCriticalStrike = largestCriticalStrike
        self.largestKillingSpree = largestKillingSpree
        self.largestMultiKill = largestMultiKill
        self.longestTimeSpentLiving = longestTimeSpentLiving
        self.magicDamageDealt = magicDamageDealt
        self.magicDamageDealtToChampions = magicDamageDealtToChampions
        self.magicDamageTaken = magicDamageTaken
        self.neutralMinionsKilled = neutralMinionsKilled
        self.nexusKills = nexusKills
        self.nexusLost = nexusLost
        self.nexusTakedowns = nexusTakedowns
        self.objectivesStolen = objectivesStolen
        self.objectivesStolenAssists = objectivesStolenAssists
        self.participantId = participantId
        self.pentaKills = pentaKills
        self.perks: PerksDto = PerksDto(**perks)
        self.physicalDamageDealt = physicalDamageDealt
        self.physicalDamageDealtToChampions = physicalDamageDealtToChampions
        self.physicalDamageTaken = physicalDamageTaken
        self.profileIcon = profileIcon
        self.puuid = puuid
        self.quadraKills = quadraKills
        self.riotIdName = riotIdName
        self.riotIdTagline = riotIdTagline
        self.role = role
        self.sightWardsBoughtInGame = sightWardsBoughtInGame
        self.spell1Casts = spell1Casts
        self.spell2Casts = spell2Casts
        self.spell3Casts = spell3Casts
        self.spell4Casts = spell4Casts
        self.summoner1Casts = summoner1Casts
        self.summoner1Id = summoner1Id
        self.summoner2Casts = summoner2Casts
        self.summoner2Id = summoner2Id
        self.summonerId = summonerId
        self.summonerLevel = summonerLevel
        self.summonerName = summonerName
        self.teamEarlySurrendered = teamEarlySurrendered
        self.teamId = teamId
        self.teamPosition = teamPosition
        self.timeCCingOthers = timeCCingOthers
        self.timePlayed = timePlayed
        self.totalDamageDealt = totalDamageDealt
        self.totalDamageDealtToChampions = totalDamageDealtToChampions
        self.totalDamageShieldedOnTeammates = totalDamageShieldedOnTeammates
        self.totalDamageTaken = totalDamageTaken
        self.totalHeal = totalHeal
        self.totalHealsOnTeammates = totalHealsOnTeammates
        self.totalMinionsKilled = totalMinionsKilled
        self.totalTimeCCDealt = totalTimeCCDealt
        self.totalTimeSpentDead = totalTimeSpentDead
        self.totalUnitsHealed = totalUnitsHealed
        self.tripleKills = tripleKills
        self.trueDamageDealt = trueDamageDealt
        self.trueDamageDealtToChampions = trueDamageDealtToChampions
        self.trueDamageTaken = trueDamageTaken
        self.turretKills = turretKills
        self.turretTakedowns = turretTakedowns
        self.turretsLost = turretsLost
        self.unrealKills = unrealKills
        self.visionScore = visionScore
        self.visionWardsBoughtInGame = visionWardsBoughtInGame
        self.wardsKilled = wardsKilled
        self.wardsPlaced = wardsPlaced
        self.win = win


class PerksDto(RiotApiResponse):
    def __init__(self, statPerks: dict, styles: List[dict], **kwargs):
        super().__init__(**kwargs)
        self.statPerks: PerkStatsDto = PerkStatsDto(**statPerks)
        self.styles: List[PerkStyleDto] = list(map(lambda x: PerkStyleDto(**x), styles))


class PerkStatsDto(RiotApiResponse):
    def __init__(self, defense: int, flex: int, offense: int, **kwargs):
        super().__init__(**kwargs)
        self.defense = defense
        self.flex = flex
        self.offense = offense


class PerkStyleDto(RiotApiResponse):
    def __init__(self, description: str, selections: List[dict], style: int, **kwargs):
        super().__init__(**kwargs)
        self.description = description
        self.selections: List[PerkStyleSelectionDto] = list(map(lambda x: PerkStyleSelectionDto(**x), selections))
        self.style = style


class PerkStyleSelectionDto(RiotApiResponse):
    def __init__(self, perk: int, var1: int, var2: int, var3: int, **kwargs):
        super().__init__(**kwargs)
        self.perk = perk
        self.var1 = var1
        self.var2 = var2
        self.var3 = var3


class TeamDto(RiotApiResponse):
    def __init__(self, bans: List[dict], objectives: dict, teamId: int, win: bool, **kwargs):
        super().__init__(**kwargs)
        self.bans: List[BanDto] = list(map(lambda x: BanDto(**x), bans))
        self.objectives: ObjectivesDto = ObjectivesDto(**objectives)
        self.teamId = teamId
        self.win = win


class BanDto(RiotApiResponse):
    def __init__(self, championId: int, pickTurn: int, **kwargs):
        super().__init__(**kwargs)
        self.championId = championId
        self.pickTurn = pickTurn


class ObjectivesDto(RiotApiResponse):
    def __init__(self, baron: dict, champion: dict, dragon: dict, inhibitor: dict, riftHerald: dict, tower: dict,
                 **kwargs):
        super().__init__(**kwargs)
        self.baron: ObjectiveDto = ObjectiveDto(**baron)
        self.champion: ObjectiveDto = ObjectiveDto(**champion)
        self.dragon: ObjectiveDto = ObjectiveDto(**dragon)
        self.inhibitor: ObjectiveDto = ObjectiveDto(**inhibitor)
        self.riftHerald: ObjectiveDto = ObjectiveDto(**riftHerald)
        self.tower: ObjectiveDto = ObjectiveDto(**tower)


class ObjectiveDto(RiotApiResponse):
    def __init__(self, first: bool, kills: int, **kwargs):
        super().__init__(**kwargs)
        self.first = first
        self.kills = kills


class MatchTimelineDto(RiotApiResponse):
    def __init__(self, metadata: dict, info: dict, **kwargs):
        super().__init__(**kwargs)
        self.metadata: MetadataDto = MetadataDto(**metadata)
        self.info: MTLInfoDto = MTLInfoDto(**info)


class MTLInfoDto(RiotApiResponse):
    def __init__(self, frameInterval: int, frames: List[dict], gameId: int, participants: List[dict], **kwargs):
        super().__init__(**kwargs)
        self.frameInterval = frameInterval
        self.frames: List[MTLFrameDto] = list(map(lambda x: MTLFrameDto(**x), frames))
        self.gameId = gameId
        self.participants: List[MTLParticipantDto] = list(map(lambda x: MTLParticipantDto(**x), participants))  # TODO


class MTLFrameDto(RiotApiResponse):
    def __init__(self, events: List[dict], participantFrames: dict, timestamp: int, **kwargs):
        super().__init__(**kwargs)
        self.events: List[MTLEventDto] = list(map(lambda x: MTLEventDto(**x), events))
        self.participantFrames: MTLParticipantFramesDto = MTLParticipantFramesDto(
            **{f'f{k}': v for k, v in participantFrames.items()}
        )
        self.timestamp = timestamp


class MTLEventDto(RiotApiResponse):
    def __init__(self, timestamp: int, type: str, levelUpType: Optional[str] = None,
                 participantId: Optional[int] = None, skillSlot: Optional[int] = None,
                 realTimestamp: Optional[int] = None, itemId: Optional[int] = None, afterId: Optional[int] = None,
                 beforeId: Optional[int] = None, goldGain: Optional[int] = None, creatorId: Optional[int] = None,
                 wardType: Optional[int] = None, assistingParticipantIds: Optional[List[int]] = None,
                 bounty: Optional[int] = None, killStreakLength: Optional[int] = None, killerId: Optional[int] = None,
                 position: Optional[dict] = None, victimDamageDealt: Optional[List[dict]] = None,
                 victimDamageReceived: Optional[List[dict]] = None, victimId: Optional[int] = None,
                 killType: Optional[int] = None, level: Optional[int] = None, multiKillLength: Optional[int] = None,
                 laneType: Optional[str] = None, teamId: Optional[int] = None, killerTeamId: Optional[int] = None,
                 monsterSubType: Optional[str] = None, monsterType: Optional[str] = None,
                 buildingType: Optional[str] = None, towerType: Optional[str] = None, name: Optional[str] = None,
                 gameId: Optional[int] = None, winningTeam: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = timestamp
        self.type = type
        self.levelUpType = levelUpType
        self.participantId = participantId
        self.skillSlot = skillSlot
        self.realTimestamp = realTimestamp
        self.itemId = itemId
        self.afterId = afterId
        self.beforeId = beforeId
        self.goldGain = goldGain
        self.creatorId = creatorId
        self.wardType = wardType
        self.assistingParticipantIds = assistingParticipantIds
        self.bounty = bounty
        self.killStreakLength = killStreakLength
        self.killerId = killerId
        self.position: Optional[MTLPositionDto] = None if position is None else MTLPositionDto(**position)
        self.victimDamageDealt: Optional[List[MTLDamageDto]] = None if victimDamageDealt is None else list(
            map(lambda x: MTLDamageDto(**x), victimDamageDealt)
        )
        self.victimDamageReceived: Optional[List[MTLDamageDto]] = None if victimDamageDealt is None else list(
            map(lambda x: MTLDamageDto(**x), victimDamageReceived)
        )
        self.victimId = victimId
        self.killType = killType
        self.level = level
        self.multiKillLength = multiKillLength
        self.laneType = laneType
        self.teamId = teamId
        self.killerTeamId = killerTeamId
        self.monsterSubType = monsterSubType
        self.monsterType = monsterType
        self.buildingType = buildingType
        self.towerType = towerType
        self.name = name
        self.gameId = gameId
        self.winningTeam = winningTeam


class MTLDamageDto(RiotApiResponse):
    def __init__(self, basic: bool, magicDamage: int, name: str, participantId: int, physicalDamage: int,
                 spellName: str, spellSlot: int, trueDamage: int, type: str, **kwargs):
        super().__init__(**kwargs)
        self.basic = basic
        self.magicDamage = magicDamage
        self.name = name
        self.participantId = participantId
        self.physicalDamage = physicalDamage
        self.spellName = spellName
        self.spellSlot = spellSlot
        self.trueDamage = trueDamage
        self.type = type


class MTLParticipantFramesDto(RiotApiResponse):
    def __init__(self, f1: dict, f2: dict, f3: dict, f4: dict, f5: dict, f6: dict, f7: dict, f8: dict, f9: dict,
                 f10: dict, **kwargs):
        super().__init__(**kwargs)
        self.f1: MTLParticipantFrameDto = MTLParticipantFrameDto(**f1)
        self.f2: MTLParticipantFrameDto = MTLParticipantFrameDto(**f2)
        self.f3: MTLParticipantFrameDto = MTLParticipantFrameDto(**f3)
        self.f4: MTLParticipantFrameDto = MTLParticipantFrameDto(**f4)
        self.f5: MTLParticipantFrameDto = MTLParticipantFrameDto(**f5)
        self.f6: MTLParticipantFrameDto = MTLParticipantFrameDto(**f6)
        self.f7: MTLParticipantFrameDto = MTLParticipantFrameDto(**f7)
        self.f8: MTLParticipantFrameDto = MTLParticipantFrameDto(**f8)
        self.f9: MTLParticipantFrameDto = MTLParticipantFrameDto(**f9)
        self.f10: MTLParticipantFrameDto = MTLParticipantFrameDto(**f10)


class MTLParticipantFrameDto(RiotApiResponse):
    def __init__(self, championStats: dict, currentGold: int, damageStats: dict, goldPerSecond: int,
                 jungleMinionsKilled: int, level: int, minionsKilled: int, participantId: int, position: dict,
                 timeEnemySpentControlled: int, totalGold: int, xp: int, **kwargs):
        super().__init__(**kwargs)
        self.championStats: MTLChampionStatsDto = MTLChampionStatsDto(**championStats)
        self.currentGold = currentGold
        self.damageStats: MTLDamageStatsDto = MTLDamageStatsDto(**damageStats)
        self.goldPerSecond = goldPerSecond
        self.jungleMinionsKilled = jungleMinionsKilled
        self.level = level
        self.minionsKilled = minionsKilled
        self.participantId = participantId
        self.position: MTLPositionDto = MTLPositionDto(**position)
        self.timeEnemySpentControlled = timeEnemySpentControlled
        self.totalGold = totalGold
        self.xp = xp


class MTLChampionStatsDto(RiotApiResponse):
    def __init__(self, abilityHaste: int, abilityPower: int, armor: int, armorPen: int, armorPenPercent: int,
                 attackDamage: int, attackSpeed: int, bonusArmorPenPercent: int, bonusMagicPenPercent: int,
                 ccReduction: int, cooldownReduction: int, health: int, healthMax: int, healthRegen: int,
                 lifesteal: int, magicPen: int, magicPenPercent: int, magicResist: int, movementSpeed: int,
                 omnivamp: int, physicalVamp: int, power: int, powerMax: int, powerRegen: int, spellVamp: int,
                 **kwargs):
        super().__init__(**kwargs)
        self.abilityHaste = abilityHaste
        self.abilityPower = abilityPower
        self.armor = armor
        self.armorPen = armorPen
        self.armorPenPercent = armorPenPercent
        self.attackDamage = attackDamage
        self.attackSpeed = attackSpeed
        self.bonusArmorPenPercent = bonusArmorPenPercent
        self.bonusMagicPenPercent = bonusMagicPenPercent
        self.ccReduction = ccReduction
        self.cooldownReduction = cooldownReduction
        self.health = health
        self.healthMax = healthMax
        self.healthRegen = healthRegen
        self.lifesteal = lifesteal
        self.magicPen = magicPen
        self.magicPenPercent = magicPenPercent
        self.magicResist = magicResist
        self.movementSpeed = movementSpeed
        self.omnivamp = omnivamp
        self.physicalVamp = physicalVamp
        self.power = power
        self.powerMax = powerMax
        self.powerRegen = powerRegen
        self.spellVamp = spellVamp


class MTLDamageStatsDto(RiotApiResponse):
    def __init__(self, magicDamageDone: int, magicDamageDoneToChampions: int, magicDamageTaken: int,
                 physicalDamageDone: int, physicalDamageDoneToChampions: int, physicalDamageTaken: int,
                 totalDamageDone: int, totalDamageDoneToChampions: int, totalDamageTaken: int, trueDamageDone: int,
                 trueDamageDoneToChampions: int, trueDamageTaken: int, **kwargs):
        super().__init__(**kwargs)
        self.magicDamageDone = magicDamageDone
        self.magicDamageDoneToChampions = magicDamageDoneToChampions
        self.magicDamageTaken = magicDamageTaken
        self.physicalDamageDone = physicalDamageDone
        self.physicalDamageDoneToChampions = physicalDamageDoneToChampions
        self.physicalDamageTaken = physicalDamageTaken
        self.totalDamageDone = totalDamageDone
        self.totalDamageDoneToChampions = totalDamageDoneToChampions
        self.totalDamageTaken = totalDamageTaken
        self.trueDamageDone = trueDamageDone
        self.trueDamageDoneToChampions = trueDamageDoneToChampions
        self.trueDamageTaken = trueDamageTaken


class MTLPositionDto(RiotApiResponse):
    def __init__(self, x: int, y: int, **kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y


class MTLParticipantDto(RiotApiResponse):
    def __init__(self, participantId: int, puuid: str, **kwargs):
        super().__init__(**kwargs)
        self.participantId = participantId
        self.puuid = puuid


# SPECTATOR-V4


class CurrentGameInfo(RiotApiResponse):
    def __init__(self, gameId: int, gameType: str, gameStartTime: int, mapId: int, gameLength: int, platformId: str,
                 gameMode: str, bannedChampions: List[dict], gameQueueConfigId: int, observers: dict,
                 participants: List[dict], **kwargs):
        super().__init__(**kwargs)
        self.gameId = gameId
        self.gameType = gameType
        self.gameStartTime = gameStartTime
        self.mapId = mapId
        self.gameLength = gameLength
        self.platformId = platformId
        self.gameMode = gameMode
        self.bannedChampions: List[BannedChampion] = list(map(lambda x: BannedChampion(**x), bannedChampions))
        self.gameQueueConfigId = gameQueueConfigId
        self.observers: Observer = Observer(**observers)
        self.participants: List[CurrentGameParticipant] = list(map(lambda x: CurrentGameParticipant(**x), participants))


class BannedChampion(RiotApiResponse):
    def __init__(self, championId: int, teamId: int, pickTurn: int, **kwargs):
        super().__init__(**kwargs)
        self.pickTurn = pickTurn
        self.championId = championId
        self.teamId = teamId


class CurrentGameParticipant(RiotApiResponse):
    def __init__(self, championId: int, perks: dict, profileIconId: int, bot: bool, teamId: int, summonerName: str,
                 summonerId: str, spell1Id: int, spell2Id: int, gameCustomizationObjects: List[dict], **kwargs):
        super().__init__(**kwargs)
        self.championId = championId
        self.perks: Perks = Perks(**perks)
        self.profileIconId = profileIconId
        self.bot = bot
        self.teamId = teamId
        self.summonerName = summonerName
        self.summonerId = summonerId
        self.spell1Id = spell1Id
        self.spell2Id = spell2Id
        self.gameCustomizationObjects: List[GameCustomizationObject] = list(
            map(lambda x: GameCustomizationObject(**x), gameCustomizationObjects)
        )


class Perks(RiotApiResponse):
    def __init__(self, perkIds: List[int], perkStyle: int, perkSubStyle: int, **kwargs):
        super().__init__(**kwargs)
        self.perkIds: List[int] = perkIds
        self.perkStyle = perkStyle
        self.perkSubStyle = perkSubStyle


class GameCustomizationObject(RiotApiResponse):
    def __init__(self, category: str, content: str, **kwargs):
        super().__init__(**kwargs)
        self.category = category
        self.content = content


class FeaturedGames(RiotApiResponse):
    def __init__(self, gameList: List[dict], clientRefreshInterval: int, **kwargs):
        super().__init__(**kwargs)
        self.gameList: List[FeaturedGameInfo] = list(map(lambda x: FeaturedGameInfo(**x), gameList))
        self.clientRefreshInterval = clientRefreshInterval


class FeaturedGameInfo(RiotApiResponse):
    def __init__(self, gameMode: str, gameLength: int, mapId: int, gameType: str, bannedChampions: List[dict],
                 gameId: int, observers: dict, gameQueueConfigId: int, gameStartTime: int, participants: List[dict],
                 platformId: str, **kwargs):
        super().__init__(**kwargs)
        self.gameMode = gameMode
        self.gameLength = gameLength
        self.mapId = mapId
        self.gameType = gameType
        self.bannedChampions: List[BannedChampion] = list(map(lambda x: BannedChampion(**x), bannedChampions))
        self.gameId = gameId
        self.gameQueueConfigId = gameQueueConfigId
        self.gameStartTime = gameStartTime
        self.participants: List[Participant] = list(map(lambda x: Participant(**x), participants))
        self.platformId = platformId
        self.observers: Observer = Observer(**observers)


class Observer(RiotApiResponse):
    def __init__(self, encryptionKey: str, **kwargs):
        super().__init__(**kwargs)
        self.encryptionKey = encryptionKey


class Participant(RiotApiResponse):
    def __init__(self, teamId: int, spell1Id: int, spell2Id: int, championId: int, profileIconId: int,
                 summonerName: str, bot: bool, **kwargs):
        super().__init__(**kwargs)
        self.teamId = teamId
        self.spell1Id = spell1Id
        self.spell2Id = spell2Id
        self.championId = championId
        self.profileIconId = profileIconId
        self.summonerName = summonerName
        self.bot = bot


# SUMMONER-V4
class SummonerDTO(RiotApiResponse):
    def __init__(self, accountId: str, profileIconId: int, revisionDate: int, name: str, id: str, puuid: str,
                 summonerLevel: int, **kwargs):
        super().__init__(**kwargs)
        self.accountId = accountId
        self.profileIconId = profileIconId
        self.revisionDate = revisionDate
        self.name = name
        self.id = id
        self.puuid = puuid
        self.summonerLevel = summonerLevel
