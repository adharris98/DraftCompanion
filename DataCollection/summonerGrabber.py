import sqlite3 as sql
import os
from threading import Thread

# this should give the user the ability to get all the summoners in high elo during a given patch
# need functions for getting the names and saving them to specific places

# need functions that:
# get all challengers from a given region
# get all grandmasters from a given region
# get all masters from a given region
# initialize the db file for a given region, within a given patch

class SummonerGrabber:
    def __init__(self, regions, ranks, queueType, watcher, patch) -> None:
        self.regions = regions  # list of the server names that players are being pulled from
        self.summonerPath = '/Users/adamharris/Documents/DraftCompanion/DataCollection/summoners/'
        self.ranks = ranks
        self.queue = queueType
        self.watcher = watcher
        self.highElo = {}
        self.patch = patch
    
    def checkDbs(self):
        for region in self.regions:
            dbFilename = self.summonerPath+self.patch+'/'+region+'.db'
            if not os.path.exists(dbFilename):
                return False
        return True

    def initializeDbs(self):
        folderPath = self.summonerPath+self.patch+'/'
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        filepaths = []
        for region in self.regions:
            filepaths.append(folderPath+region+'.db')
        for filepath in filepaths:
            with sql.connect(filepath) as db:
                c = db.cursor()
                for rank in self.ranks:
                    c.execute(f'''CREATE table IF NOT EXISTS {rank} (
                    accountName text NOT NULL,
                    id text PRIMARY KEY,
                    accountID text NOT NULL,
                    puuid text NOT NULL
                    );''')
                    db.commit()
                c.close()
    
    def getSummonerNames(self):
        # need to ask riot for the data from each rank for each region
        # then go through each server and save all the data gathered
        # then lookup each individuals name and get their information
        challengers = {}
        grandmasters = {}
        masters = {}
        for region in self.regions:
            print(f'Fetching challengers for {region}')
            fullChall = self.watcher.league.challenger_by_queue(region=region, queue=self.queue)
            challengers[region] = fullChall['entries']
            print(f'Fetching grandmasters for {region}')
            fullGm = self.watcher.league.grandmaster_by_queue(region=region, queue=self.queue)
            grandmasters[region] = fullGm['entries']
            print(f'Fetching masters for {region}')
            fullMasters = self.watcher.league.masters_by_queue(region=region, queue=self.queue)
            masters[region] = fullMasters['entries']
        self.highElo['challenger'] = challengers
        self.highElo['grandmaster'] = grandmasters
        self.highElo['master'] = masters
    
    def saveIDs(self, summoners, region, rank):
        dbFilepath = self.summonerPath + self.patch + '/' + region + '.db'
        if not os.path.exists(dbFilepath):
            raise FileNotFoundError
        with sql.connect(dbFilepath) as db:
            c = db.cursor()
            for summoner in summoners:
                data = (summoner['name'], summoner['id'], summoner['accountId'], summoner['puuid'])
                execute_string = f'INSERT into {rank} VALUES(?, ?, ?, ?);'
                try:
                    c.execute(execute_string, data)
                    db.commit
                except:
                    print(f'save    : Problem inserting {data[0]}\'s data into the database',end='\r')
    
    def printName(self, name, region):
        empty = '-'
        order = ['','','','']
        for i in range(4):
            if self.regions[i] == region:
                order[i] = name
            else:
                order[i] = empty
        print(f'|{order[0]:^25}|{order[1]:^25}|{order[2]:^25}|{order[3]:^25}|', end='\r')
    
    def getIDsByRegion(self, region, players, rank):
        # print(f'Gathering IDs for {region}')
        summonerData = []
        # for player in players[:2]:
        for player in players:
            name = player['summonerName']
            self.printName(name, region)
            try:
                summonerData.append(self.watcher.summoner.by_name(region, name))
                self.saveIDs(summonerData, region, rank)
            except:
                print(f'get     : Unable to fetch data for {name}',end='\r')
    
    def getIDs(self):
        # The incoming highElo dictionary is separated by rank and then region
        # rate limits are for each region so pull the results at the same time
        print(f'|{self.regions[0]:^25}|{self.regions[1]:^25}|{self.regions[2]:^25}|{self.regions[3]:^25}|')
        for rank in self.ranks:
            players = self.highElo[rank]
            # print(f'|{rank:^83}|')
            threads = list()
            for region in self.regions:
                t = Thread(target=self.getIDsByRegion, args=(region,players[region],rank))
                threads.append(t)
                t.start()
            for t in threads:
                t.join()
        print()

    # def getIDsTest(self, highElo):
    #     # The incoming highElo dictionary is separated by rank and then region
    #     # rate limits are for each region so pull the results at the same time
    #     for rank in self.ranks:
    #         players = highElo[rank]
    #         print(f'|{self.regions[0]:^25}|{self.regions[1]:^25}|{self.regions[2]:^25}|{self.regions[3]:^25}|')
    #         threads = list()
    #         for region in self.regions:
    #             t = Thread(target=self.getIDsByRegion, args=(region,players[region],rank))
    #             threads.append(t)
    #             t.start()
    #         for region,t in zip(self.regions,threads):
    #             t.join()
    
    def run(self):
        # Runs all the functions needed to gather IDs from highElo players
        # first, check if the databases exist or if they need to be initialized
        if not self.checkDbs():
            self.initializeDbs()
        
        # next, get the summoner names
        self.getSummonerNames()

        # finally, get the IDs and save them
        self.getIDs()