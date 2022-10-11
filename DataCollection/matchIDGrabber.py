import sqlite3 as sql
import os
from threading import Thread
from calendar import timegm


class MatchIDGrabber:
    def __init__(self, regions, continents, ranks, queueID, watcher, patch, startDate) -> None:
        self.regions = regions  # list of the server names that players are being pulled from
        self.continents = continents
        self.summonerPath = '/Users/adamharris/Documents/DraftCompanion/DataCollection/summoners/'
        self.matchPath = '/Users/adamharris/Documents/DraftCompanion/DataCollection/matchIDs/'
        self.ranks = ranks
        self.queue = queueID
        self.watcher = watcher
        self.patch = patch
        self.startPatch = timegm(startDate.timetuple())
        self.matchlistErrors = 0
        self.executeErrors = 0
    
    def checkDbs(self):
        for region in self.regions:
            dbFilename = self.matchPath+self.patch+'/'+region+'.db'
            if not os.path.exists(dbFilename):
                return False
        return True

    def initializeDbs(self):
        folderPath = self.matchPath+self.patch+'/'
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        filepaths = []
        for region in self.regions:
            filepaths.append(folderPath+region+'.db')
        for filepath in filepaths:
            with sql.connect(filepath) as db:
                c = db.cursor()
                c.execute(f'''CREATE table IF NOT EXISTS IDs (
                accountName text NOT NULL,
                matchID text PRIMARY KEY,
                rank text NOT NULL
                );''')
                db.commit()
                c.close()
    
    def getSummonerData(self, summonerDb):
        # this accesses the db given by summonerDb and then returns the collected data
        summonerData = dict()
        with sql.connect(summonerDb) as db:
            c = db.cursor()
            for rank in self.ranks:
                execute_statement = f'SELECT accountName,puuid from {rank}'
                rows = c.execute(execute_statement).fetchall()
                summonerData[rank] = rows
        return summonerData

    def getPlayerMatchlists(self, summonerData, matchIdDb, region):
        # pull the matchlists for each player, and add them all to the same db
        with sql.connect(matchIdDb) as db:
            c = db.cursor()
            for rank in self.ranks:
                for name, puuid in summonerData[rank]:
                    matchList = list()
                    try:
                        print(f'Gathering matchlist from ({region},{rank}) for {name:<30}',end='\r')
                        matchList = self.watcher.match.matchlist_by_puuid(region=self.continents[region], puuid=puuid, start_time=self.startPatch, queue=self.queue, count=100)
                    except:
                        self.matchlistErrors += 1
                        print(f'[#{self.matchlistErrors}]: Unable to get matches for {name:<30}',end='\r')
                    for matchid in matchList:
                        execute_data = (name, matchid, rank)
                        execute_string = f'INSERT INTO IDs (accountName,matchID,rank) VALUES(?,?,?)'
                        try:
                            c.execute(execute_string,execute_data)
                            db.commit()
                        except sql.IntegrityError:
                            self.executeErrors += 1
                            print(f'[#{self.executeErrors}]: MatchID already added via another summoner',end='\r')
                        except:
                            print(f'Another error occurred',end='\r')

    def threadedMatchGetter(self, summonerDb, region):
        # now the process for each region should be the same
        # first, get the info from all the gathered summoners
        summonerDb += region+'.db'
        summonerData = self.getSummonerData(summonerDb)

        # then, get the matchlist for each player and add it to the proper db
        matchIdDb = self.matchPath+self.patch+'/'+region+'.db'
        self.getPlayerMatchlists(summonerData, matchIdDb, region)
    
    def setupMatchGetter(self):
        # this function sets up the multithreading for the process
        # there should be a thread for each region in self.regions
        summonerDb = self.summonerPath+self.patch+'/'
        threads = list()
        for region in self.regions:
            t = Thread(target=self.threadedMatchGetter, args=(summonerDb, region))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
    
    def run(self):
        if not self.checkDbs():
            self.initializeDbs()
        self.setupMatchGetter()