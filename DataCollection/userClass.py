# this file containes the user class which streamlines the riot watcher setup process
from riotwatcher import LolWatcher

class User:
    def __init__(self, region:str, continent:str, name:str) -> None:
        self.api_key = ''
        self.region = region
        self.continent = continent
        self.summoner = name

    def getWatcher(self):
        return LolWatcher(self.api_key)

    def getRegion(self):
        return self.region

    def getContinent(self):
        return self.continent

    def getSummoner(self):
        return self.summoner