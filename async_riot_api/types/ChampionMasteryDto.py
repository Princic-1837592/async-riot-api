class ChampionMasteryDto:
    def __init__(self, championPointsUntilNextLevel: int, chestGranted: bool, championId: int, lastPlayTime: int,
                 championLevel: int, summonerId: str, championPoints: int, championPointsSinceLastLevel: int,
                 tokensEarned: int):
        self.championPointsUntilNextLevel = championPointsUntilNextLevel
        self.chestGranted = chestGranted
        self.championId = championId
        self.lastPlayTime = lastPlayTime
        self.championLevel = championLevel
        self.summonerId = summonerId
        self.championPoints = championPoints
        self.championPointsSinceLastLevel = championPointsSinceLastLevel
        self.tokensEarned = tokensEarned
