from operator import truediv
import re
import sqlite3 as sql
import os
from threading import Thread
from calendar import timegm
from LoLClasses import MatchInfo


class MatchParser:
    def __init__(self, regions, continents, ranks, watcher, patch) -> None:
        self.regions = regions  # list of the server names that players are being pulled from
        self.continents = continents
        self.matchIdPath = '/Users/adamharris/Documents/DraftCompanion/DataCollection/matchIDs/'
        self.matchDataPath = '/Users/adamharris/Documents/DraftCompanion/DataCollection/matchData/'
        self.ranks = ranks
        self.watcher = watcher
        self.patch = patch
        self.progress = {
            'EUN1' : '',
            'EUW1' : '',
            'KR'   : '',
            'NA1'  : ''
        }
    
    def checkDbs(self):
        for region in self.regions:
            dbFilename = self.matchDataPath+self.patch+'/'+region+'.db'
            if not os.path.exists(dbFilename):
                return False
        return True

    def initializeDbs(self):
        folderPath = self.matchDataPath+self.patch+'/'
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        for region in self.regions:
            filepath = folderPath+region+'.db'
            with sql.connect(filepath) as db:
                c = db.cursor()
                for rank in self.ranks:
                    c.execute(f'''CREATE table IF NOT EXISTS {rank}(
                    match_id text PRIMARY KEY,
                    winner text NOT NULL,
                    red_top text NOT NULL,
                    red_jungle text NOT NULL,
                    red_mid text NOT NULL,
                    red_bot text NOT NULL,
                    red_support text NOT NULL,
                    blue_top text NOT NULL,
                    blue_jungle text NOT NULL,
                    blue_mid text NOT NULL,
                    blue_bot text NOT NULL,
                    blue_support text NOT NULL
                    );''')
                    db.commit()
                c.close()
    
    def printProgress(self):
        order = ['','','','']
        for i in range(len(self.regions)):
            order[i] = self.progress[self.regions[i]]
        print(f'|{order[0]:^25}|{order[1]:^25}|{order[2]:^25}|{order[3]:^25}|', end='\r')
    
    def writeMatchDataToDatabase(self, cursor, matchData:MatchInfo, rank):
        data = matchData.convert_to_db_tuple()
        execute_string = f'INSERT into {rank} VALUES(?,?,?,?,?,?,?,?,?,?,?,?);'
        cursor.execute(execute_string, data)
    
    def getIndividualMatchData(self, matchId, region):
        rawMatchData = self.watcher.match.by_id(region=self.continents[region], match_id=matchId)
        return MatchInfo(rawMatchData)
    
    def getMatchIds(self, matchIdDb):
        matchIds = dict()
        with sql.connect(matchIdDb) as db:
            c = db.cursor()
            for rank in self.ranks:
                execute_string = f'SELECT matchID from IDs WHERE rank = ?;'
                rows = c.execute(execute_string, (rank,)).fetchall()
                matchIds[rank] = []
                for row in rows:
                    matchIds[rank].append(row[0])
        return matchIds
    
    def pullMatchData(self, matchIds, matchDataDb, region):
        with sql.connect(matchDataDb) as db:
            c = db.cursor()
            for rank in self.ranks:
                rankIds = matchIds[rank]
                size = len(rankIds)
                count = 0
                # rr = region+' : '+rank
                # print(f'|{rr:^83}|')
                # print(f'|{self.regions[0]:^25}|{self.regions[1]:^25}|{self.regions[2]:^25}|{self.regions[3]:^25}|')
                for rankId in rankIds:
                    count += 1
                    self.progress[region] = f'{rank}: {count} / {size}'
                    self.printProgress()
                    try:
                        matchData = self.getIndividualMatchData(rankId, region)
                    except:
                        print(f'Problem loading data for {rankId:<60}',end='\r')
                    try:
                        self.writeMatchDataToDatabase(c, matchData, rank)
                        db.commit()
                    except:
                        print('This match has already been processed',end='\r')
    
    def threadedMatchParsing(self, matchIdDb, matchDataDb, region):
        # first, gather all the collected match IDs and separate them by rank
        matchIdDb += region+'.db'
        matchIds = self.getMatchIds(matchIdDb)
        # Now that we have all the match ids, get their data by rank and add them to the proper db
        matchDataDb += region+'.db'
        self.pullMatchData(matchIds, matchDataDb, region)

    def setupMatchParser(self):
        # this function sets up the multithreading for the process
        # there should be a thread for each region in self.regions
        # remember the ID dbs are structured differently
        matchIdDb = self.matchIdPath+self.patch+'/'
        matchDataDb = self.matchDataPath+self.patch+'/'
        threads = list()
        print(f'|{self.regions[0]:^25}|{self.regions[1]:^25}|{self.regions[2]:^25}|{self.regions[3]:^25}|',end='\r')
        for region in self.regions:
            t = Thread(target=self.threadedMatchParsing, args=(matchIdDb, matchDataDb, region))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        print()
    
    def run(self):
        if not self.checkDbs():
            self.initializeDbs()
        self.setupMatchParser()