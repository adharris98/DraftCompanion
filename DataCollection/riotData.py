# This file contains helper functions that get data from the Riot API
from riotwatcher import LolWatcher

class Riot:
    def __init__(self) -> None:
        self.regions = ['EUN1','EUW1','KR','NA1']
        self.continents = {
            'EUN1' : 'EUROPE',
            'EUW1' : 'EUROPE',
            'KR'   : 'ASIA',
            'NA1'  : 'AMERICAS'
        }
        self.rankedQueueID = 420
        self.ranks = ['challenger', 'grandmaster', 'master']
        self.queueType = 'RANKED_SOLO_5x5'
    
    def checkPatch(self, patch):
        if 'patch' in patch:
            # print('Not in correct format')
            patch = patch.split('_')
            patch = patch[1]+'.'+patch[2]+'.1'
        return patch

    def getVersions(self, watcher:LolWatcher.data_dragon):
        return watcher.versions_all()
    
    def getChampionStatList(self, watcher:LolWatcher, patch:str, Full=False):
        patch = self.checkPatch(patch)
        championList = watcher.data_dragon.champions(patch)
        return championList['data']
    
    def getChampionNames(self, watcher, patch):
        patch = self.checkPatch(patch)
        championStatList = self.getChampionStatList(watcher, patch)
        return list(championStatList.keys())
    
    def getChampionStats(self, championStatList):
        championStats = []
        for champion in championStatList:
            stats = dict({champion : championStatList[champion]['stats']})
            championStats.append(stats)
        return championStats
    
    def getRegions(self):
        return self.regions
    
    def getContinents(self):
        return self.continents
    
    def getQueueID(self):
        return self.rankedQueueID
    
    def getRanks(self):
        return self.ranks
    
    def getQueueType(self):
        return self.queueType