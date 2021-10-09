from typing import List, Optional


class RiotApiResponse:
    def __init__(self, succeed: bool = True):
        self.succeed = succeed
        self.error = not succeed
    
    def __str__(self):
        return '{}({})'.format(
            type(self).__name__,
            ', '.join('{} = {}'.format(*item) for item in vars(self).items())
        )
    
    def __repr__(self):
        return str(self)


class SummonerDTO(RiotApiResponse):
    def __init__(self, accountId: str, profileIconId: int, revisionDate: int, name: str, id: str, puuid: str,
                 summonerLevel: int):
        super().__init__()
        self.accountId = accountId
        self.profileIconId = profileIconId
        self.revisionDate = revisionDate
        self.name = name
        self.id = id
        self.puuid = puuid
        self.summonerLevel = summonerLevel


class ChampionMasteryDto(RiotApiResponse):
    def __init__(self, championPointsUntilNextLevel: int, chestGranted: bool, championId: int, lastPlayTime: int,
                 championLevel: int, summonerId: str, championPoints: int, championPointsSinceLastLevel: int,
                 tokensEarned: int):
        super().__init__()
        self.championPointsUntilNextLevel = championPointsUntilNextLevel
        self.chestGranted = chestGranted
        self.championId = championId
        self.lastPlayTime = lastPlayTime
        self.championLevel = championLevel
        self.summonerId = summonerId
        self.championPoints = championPoints
        self.championPointsSinceLastLevel = championPointsSinceLastLevel
        self.tokensEarned = tokensEarned


class ChampionInfo(RiotApiResponse):
    def __init__(self, maxNewPlayerLevel: int, freeChampionIdsForNewPlayers: List[int], freeChampionIds: List[int]):
        super().__init__()
        self.maxNewPlayerLevel = maxNewPlayerLevel
        self.freeChampionIdsForNewPlayers = freeChampionIdsForNewPlayers
        self.freeChampionIds = freeChampionIds


class LeagueEntryDTO(RiotApiResponse):
    def __init__(self, leagueId: str, summonerId: str, summonerName: str, queueType: str, tier: str, rank: str,
                 leaguePoints: int, wins: int, losses: int, hotStreak: bool, veteran: bool, freshBlood: bool,
                 inactive: bool, miniSeries: Optional[dict] = None):
        super().__init__()
        self.leagueId = leagueId
        self.summonerId = summonerId
        self.summonerName = summonerName
        self.queueType = queueType
        self.tier = tier
        self.rank = rank
        self.leaguePoints = leaguePoints
        self.wins = wins
        self.losses = losses
        self.hotStreak = hotStreak
        self.veteran = veteran
        self.freshBlood = freshBlood
        self.inactive = inactive
        self.miniSeries: Optional[MiniSeriesDTO] = None if miniSeries is None else MiniSeriesDTO(**miniSeries)
        self.short: str = LeagueEntryDTO.__get_short(self.tier, self.rank)
    
    @staticmethod
    def __get_short(tier: str, rank: str) -> str:
        return f"{('GM' if tier.startswith('GR') else tier[0])}{'4' if rank.lower().endswith('v') else len(rank)}"


class MiniSeriesDTO(RiotApiResponse):
    def __init__(self, losses: int, progress: str, target: int, wins: int):
        super().__init__()
        self.losses = losses
        self.progress = progress
        self.target = target
        self.wins = wins


class ShardStatus(RiotApiResponse):
    def __init__(self, name: str, slug: str, locales: List[str], hostname: str, region_tag: str, services: List[dict]):
        super().__init__()
        self.name = name
        self.slug = slug
        self.locales = locales
        self.hostname = hostname
        self.region_tag = region_tag
        self.services: List[Service] = list(map(lambda x: Service(**x), services))


class Service(RiotApiResponse):
    def __init__(self, name: str, slug: str, status: str, incidents: List[dict]):
        super().__init__()
        self.name = name
        self.slug = slug
        self.status = status
        self.incidents: List[Incident] = list(map(lambda x: Incident(**x), incidents))


class Incident(RiotApiResponse):
    def __init__(self, id: int, active: bool, created_at: str, updates: List[dict]):
        super().__init__()
        self.id = id
        self.active = active
        self.created_at = created_at
        self.updates: List[Message] = list(map(lambda x: Message(**x), updates))


class Message(RiotApiResponse):
    def __init__(self, id: str, author: str, heading: str, content: str, severity: str, created_at: str,
                 updated_at: str, translations: List[dict]):
        super().__init__()
        self.id = id
        self.author = author
        self.heading = heading
        self.content = content
        self.severity = severity
        self.created_at = created_at
        self.updated_at = updated_at
        self.translations: List[Translation] = list(map(lambda x: Translation(**x), translations))


class Translation(RiotApiResponse):
    def __init__(self, locale: str, heading: str, content: str):
        super().__init__()
        self.locale = locale
        self.heading = heading
        self.content = content


class PlatformDataDto(RiotApiResponse):
    def __init__(self, id: str, name: str, locales: List[str], maintenances: List[dict], incidents: List[dict]):
        super().__init__()
        self.id = id
        self.name = name
        self.locales = locales
        self.maintenances: List[StatusDto] = list(map(lambda x: StatusDto(**x), maintenances))
        self.incidents: List[StatusDto] = list(map(lambda x: StatusDto(**x), incidents))


class StatusDto(RiotApiResponse):
    def __init__(self, id: int, maintenance_status: str, incident_severity: Optional[str], titles: List[dict],
                 updates: List[dict], created_at: str, archive_at: str, updated_at: Optional[str],
                 platforms: List[str]):
        super().__init__()
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
    def __init__(self, locale: str, content: str):
        super().__init__()
        self.locale = locale
        self.content = content


class UpdateDto(RiotApiResponse):
    def __init__(self, id: int, author: str, publish: bool, publish_locations: List[str], translations: List[dict],
                 created_at: str, updated_at: str):
        super().__init__()
        self.id = id
        self.author = author
        self.publish = publish
        self.publish_locations = publish_locations
        self.translations: List[ContentDto] = list(map(lambda x: ContentDto(**x), translations))
        self.created_at = created_at
        self.updated_at = updated_at


class MatchDto(RiotApiResponse):
    def __init__(self, metadata: dict, info: dict):
        super().__init__()
        self.metadata: MetadataDto = MetadataDto(**metadata)
        self.info: InfoDto = InfoDto(**info)


class MetadataDto(RiotApiResponse):
    def __init__(self, dataVersion: str, matchId: str, participants: List[str]):
        super().__init__()
        self.dataVersion = dataVersion
        self.matchId = matchId
        self.participants = participants


class InfoDto(RiotApiResponse):
    def __init__(self, gameCreation: int, gameDuration: int, gameId: int, gameMode: str, gameName: str,
                 gameStartTimestamp: int, gameType: str, gameVersion: str, mapId: int, participants: List[str],
                 platformId: str, queueId: int, teams: List[dict], tournamentCode: Optional[str] = None,
                 gameEndTimestamp: int = 0):
        super().__init__()
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
                 individualPosition: str, inhibitorKills: int, inhibitorTakedowns: int, inhibitorsLost: int, item0: int,
                 item1: int, item2: int, item3: int, item4: int, item5: int, item6: int, itemsPurchased: int,
                 killingSprees: int, kills: int, lane: str, largestCriticalStrike: int, largestKillingSpree: int,
                 largestMultiKill: int, longestTimeSpentLiving: int, magicDamageDealt: int,
                 magicDamageDealtToChampions: int, magicDamageTaken: int, neutralMinionsKilled: int, nexusKills: int,
                 nexusLost: int, nexusTakedowns: int, objectivesStolen: int, objectivesStolenAssists: int,
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
                 turretKills: int, turretTakedowns: int, turretsLost: int, unrealKills: int, visionScore: int,
                 visionWardsBoughtInGame: int, wardsKilled: int, wardsPlaced: int, win: bool):
        super().__init__()
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
    def __init__(self, statPerks: dict, styles: List[dict]):
        super().__init__()
        self.statPerks: PerkStatsDto = PerkStatsDto(**statPerks)
        self.styles: List[PerkStyleDto] = list(map(lambda x: PerkStyleDto(**x), styles))


class PerkStatsDto(RiotApiResponse):
    def __init__(self, defense: int, flex: int, offense: int):
        super().__init__()
        self.defense = defense
        self.flex = flex
        self.offense = offense


class PerkStyleDto(RiotApiResponse):
    def __init__(self, description: str, selections: List[dict], style: int):
        super().__init__()
        self.description = description
        self.selections: List[PerkStyleSelectionDto] = list(map(lambda x: PerkStyleSelectionDto(**x), selections))
        self.style = style


class PerkStyleSelectionDto(RiotApiResponse):
    def __init__(self, perk: int, var1: int, var2: int, var3: int):
        super().__init__()
        self.perk = perk
        self.var1 = var1
        self.var2 = var2
        self.var3 = var3


class TeamDto(RiotApiResponse):
    def __init__(self, bans: List[dict], objectives: dict, teamId: int, win: bool):
        super().__init__()
        self.bans: List[BanDto] = list(map(lambda x: BanDto(**x), bans))
        self.objectives: ObjectivesDto = ObjectivesDto(**objectives)
        self.teamId = teamId
        self.win = win


class BanDto(RiotApiResponse):
    def __init__(self, championId: int, pickTurn: int):
        super().__init__()
        self.championId = championId
        self.pickTurn = pickTurn


class ObjectivesDto(RiotApiResponse):
    def __init__(self, baron: dict, champion: dict, dragon: dict, inhibitor: dict, riftHerald: dict, tower: dict):
        super().__init__()
        self.baron: ObjectiveDto = ObjectiveDto(**baron)
        self.champion: ObjectiveDto = ObjectiveDto(**champion)
        self.dragon: ObjectiveDto = ObjectiveDto(**dragon)
        self.inhibitor: ObjectiveDto = ObjectiveDto(**inhibitor)
        self.riftHerald: ObjectiveDto = ObjectiveDto(**riftHerald)
        self.tower: ObjectiveDto = ObjectiveDto(**tower)


class ObjectiveDto(RiotApiResponse):
    def __init__(self, first: bool, kills: int):
        super().__init__()
        self.first = first
        self.kills = kills


class CurrentGameInfo(RiotApiResponse):
    def __init__(self, gameId: int, gameType: str, gameStartTime: int, mapId: int, gameLength: int, platformId: str,
                 gameMode: str, bannedChampions: List[dict], gameQueueConfigId: int, observers: dict,
                 participants: List[dict]):
        super().__init__()
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
    def __init__(self, championId: int, teamId: int, pickTurn: int):
        super().__init__()
        self.pickTurn = pickTurn
        self.championId = championId
        self.teamId = teamId


class CurrentGameParticipant(RiotApiResponse):
    def __init__(self, championId: int, perks: dict, profileIconId: int, bot: bool, teamId: int, summonerName: str,
                 summonerId: str, spell1Id: int, spell2Id: int, gameCustomizationObjects: List[dict]):
        super().__init__()
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
    def __init__(self, perkIds: List[int], perkStyle: int, perkSubStyle: int):
        super().__init__()
        self.perkIds: List[int] = perkIds
        self.perkStyle = perkStyle
        self.perkSubStyle = perkSubStyle


class GameCustomizationObject(RiotApiResponse):
    def __init__(self, category: str, content: str):
        super().__init__()
        self.category = category
        self.content = content


class FeaturedGames(RiotApiResponse):
    def __init__(self, gameList: List[dict], clientRefreshInterval: int):
        super().__init__()
        self.gameList: List[FeaturedGameInfo] = list(map(lambda x: FeaturedGameInfo(**x), gameList))
        self.clientRefreshInterval = clientRefreshInterval


class FeaturedGameInfo(RiotApiResponse):
    def __init__(self, gameMode: str, gameLength: int, mapId: int, gameType: str, bannedChampions: List[dict],
                 gameId: int, observers: dict, gameQueueConfigId: int, gameStartTime: int, participants: List[dict],
                 platformId: str):
        super().__init__()
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
    def __init__(self, encryptionKey: str):
        super().__init__()
        self.encryptionKey = encryptionKey


class Participant(RiotApiResponse):
    def __init__(self, teamId: int, spell1Id: int, spell2Id: int, championId: int, profileIconId: int,
                 summonerName: str, bot: bool):
        super().__init__()
        self.teamId = teamId
        self.spell1Id = spell1Id
        self.spell2Id = spell2Id
        self.championId = championId
        self.profileIconId = profileIconId
        self.summonerName = summonerName
        self.bot = bot


class RiotApiError(RiotApiResponse):
    def __init__(self, message: str = 'Bad Request', status_code: int = 400):
        super().__init__(False)
        self.message = message
        self.status_code = status_code
