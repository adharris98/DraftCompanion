import sqlite3 as sql
import os
from threading import Thread
from pprint import pprint as pp
import LoLClasses as lc


class ChampionDataParser:
    def __init__(self, regions, ranks, patch, champNames) -> None:
        self.regions = regions
        self.ranks = ranks
        self.patch = patch
        self.championDataPath = '/Users/adamharris/Documents/DraftCompanion/WebApp/data/champions/'
        self.matchDataPath = '/Users/adamharris/Documents/DraftCompanion/DataCollection/matchData/'
        self.testDbPath = '/Users/adamharris/Documents/DraftCompanion/DataCollection/matchData/patch_12_18/testDataset.db'
        self.tableTypes = ['versus', 'allied']
        self.rankAbrev = {
            'challenger' : 'c',
            'grandmaster' : 'gm',
            'master' : 'm'
        }
        self.rankIndex = {
            'challenger'  : 0,
            'grandmaster' : 1,
            'master'      : 2
        }
        self.numMatches = {
            'EUN1' : [0,0,0],
            'EUW1' : [0,0,0],
            'KR'   : [0,0,0],
            'NA1'  : [0,0,0]
        }
        self.matchesComplete = {
            'EUN1' : 0,
            'EUW1' : 0,
            'KR'   : 0,
            'NA1'  : 0
        }
        self.progress = {
            'EUN1' : ['','',''],
            'EUW1' : ['','',''],
            'KR'   : ['','',''],
            'NA1'  : ['','','']
        }
        self.champions = champNames
        self.testDataset = list()
    
    def printProgress(self):
        order = ['','','','']
        for i,region in enumerate(self.regions):
            regionSum = sum(self.numMatches[region])
            regionDone = self.matchesComplete[region]
            order[i] = f'{region} : {regionDone} / {regionSum}'
        print(f'|{order[0]:^20}|{order[1]:^20}|{order[2]:^20}|{order[3]:^20}|', end='\r')
    
    def createTestDataset(self):
        with sql.connect(self.testDbPath) as db:
            c = db.cursor()
            c.execute(f'''CREATE table IF NOT EXISTS testDataset (
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
    
    def checkDbs(self):
        for tableType in self.tableTypes:
            dbFilename = self.championDataPath+self.patch+'/'+tableType+'.db'
            if not os.path.exists(dbFilename):
                return False
        return True
    
    def initializeDbs(self):
        folderPath = self.championDataPath+self.patch+'/'
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        for tableType in self.tableTypes:
            filepath = folderPath+tableType+'.db'
            with sql.connect(filepath) as db:
                c = db.cursor()
                for name in self.champions:
                    print(f'Creating {tableType} table for {name:15}', end='\r')
                    c.execute(f'''CREATE table IF NOT EXISTS {name}(
                    {tableType} text PRIMARY KEY,
                    KR_c_w integer NOT NULL,    KR_c_l integer NOT NULL,
                    KR_gm_w integer NOT NULL,   KR_gm_l integer NOT NULL,
                    KR_m_w integer NOT NULL,    KR_m_l integer NOT NULL,
                    NA1_c_w  integer NOT NULL,  NA1_c_l  integer NOT NULL,
                    NA1_gm_w  integer NOT NULL, NA1_gm_l  integer NOT NULL,
                    NA1_m_w  integer NOT NULL,  NA1_m_l  integer NOT NULL,
                    EUN1_c_w integer NOT NULL,  EUN1_c_l integer NOT NULL,
                    EUN1_gm_w integer NOT NULL, EUN1_gm_l integer NOT NULL,
                    EUN1_m_w integer NOT NULL,  EUN1_m_l integer NOT NULL,
                    EUW1_c_w integer NOT NULL,  EUW1_c_l integer NOT NULL,
                    EUW1_gm_w integer NOT NULL, EUW1_gm_l integer NOT NULL,
                    EUW1_m_w integer NOT NULL,  EUW1_m_l integer NOT NULL);''')
                    db.commit()
                    for newName in self.champions:
                        execute_string = f'INSERT INTO {name} VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
                        execute_data = (newName, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
                        c.execute(execute_string, execute_data)
                        db.commit()
    
    def createChampionDataDictionary(self) -> dict:
        data = dict()
        for name in self.champions:
            data.update({name : {}})    # initializing the dict with champion names
            for compare in self.champions:
                # initializing the dict with the champions who are being compared to the champion 'name'
                # compare : [wins,losses]
                data[name].update({compare : [0,0]})
        return data
    
    def writeToTestDatasetDb(self):
        with sql.connect(self.testDbPath) as db:
            c = db.cursor()
            for testMatch in self.testDataset:
                execute_string = 'INSERT INTO testDataset VALUES(?,?,?,?,?,?,?,?,?,?,?,?);'
                c.execute(execute_string, testMatch)
                db.commit()

    def writeToChampDb(self, champDb:str, data:dict, region:str, rank:str, mode:str):
        rankAbr = self.rankAbrev[rank]
        winColumn  = region+'_'+rankAbr+'_w'
        lossColumn = region+'_'+rankAbr+'_l'
        with sql.connect(champDb) as db:
            c = db.cursor()
            for key, _ in data.items():
                for name in self.champions:
                    execute_data = (data[key][name][0], data[key][name][1], name)
                    execute_string = f'UPDATE {key} SET {winColumn} = ?, {lossColumn} = ? WHERE {mode} = ?;'
                    c.execute(execute_string, execute_data)
                    db.commit()
    
    def parseData(self, matchFolder:str, champFolder:str, region:str, rank:str):
        # print(f'Parsing match data for {rank} rank in {region} region\n')
        rankI = self.rankIndex[rank]
        
        rankWeight = 1
        # if rank == 'challenger':
        #     rankWeight = 3
        # elif rank == 'grandmaster':
        #     rankWeight = 2
        # else:
        #     rankWeight = 1

        # this does the versus and allied match parsing and saving for each rank in each region
        # data[0] is versus, data[1] is allied
        data = [self.createChampionDataDictionary(), self.createChampionDataDictionary()]
        
        # define the database where the data will be extracted from
        matchDb = matchFolder+region+'.db'      # has three tables, challenger, grandmaster, master

        # now open the database and pull the data from the three tables
        # first, setup a variable to hold all the data
        matchData = list()
        with sql.connect(matchDb) as db:
            c = db.cursor()
            execute_string = f'SELECT * from {rank};'
            matchData = c.execute(execute_string).fetchall()
            self.numMatches[region][rankI] = len(matchData)
        # print(self.numMatches)

        # second, iterate over the match data and perform versus and allied collection
        # red_i,blue_i = 0,0  # determine whether the wins or losses columns are being incremented
        for i, match in enumerate(matchData):
            # self.progress[region][rankI] = f'{i} / {self.numMatches[region][rankI]}'
            self.printProgress()
            if not i%5:     # add this match to the test dataset (should get ~20% of all matches)
                # print('Adding to test Dataset')
                if '' not in match:
                    self.testDataset.append(match)
            else:
                # if (region == 'KR') and ('Aatrox' in match) and ('Yorick' in match):
                #     print(match)
                if '' not in match:
                    _, winner, red_top, red_jg, red_mid, red_adc, red_sup, blue_top, blue_jg, blue_mid, blue_adc, blue_sup = match
                    red_side = [red_top, red_jg, red_mid, red_adc, red_sup]
                    blue_side = [blue_top, blue_jg, blue_mid, blue_adc, blue_sup]
                    # if winner == 'red':
                    #     red_i = 0
                    #     blue_i = 1
                    # else:
                    #     red_i = 1
                    #     blue_i = 0
                    for red in red_side:
                        # print(red)
                        if winner == 'red':
                            for ally,versus in zip(red_side, blue_side):
                                data[0][red][versus][0] += rankWeight
                                data[1][red][ally][0] += rankWeight
                        else:
                            for ally,versus in zip(red_side, blue_side):
                                data[0][red][versus][1] += rankWeight
                                data[1][red][ally][1] += rankWeight
                            # data[0][red][versus][red_i] += 1
                            # data[1][red][ally][red_i] += 1
                    for blue in blue_side:
                        # print(blue)
                        if winner == 'blue':
                            for ally,versus in zip(blue_side, red_side):
                                data[0][blue][versus][0] += rankWeight
                                data[1][blue][ally][0] += rankWeight
                        else:
                            for ally,versus in zip(blue_side, red_side):
                                data[0][blue][versus][1] += rankWeight
                                data[1][blue][ally][1] += rankWeight
                            # data[0][blue][versus][blue_i] += 1
                            # data[1][blue][ally][blue_i] += 1
            self.matchesComplete[region] += 1
        
        for j,mode in enumerate(self.tableTypes):
            champDbFile = champFolder+mode+'.db'
            self.writeToChampDb(champDb=champDbFile, data=data[j], region=region, rank=rank, mode=mode)
        # print(f'            Finished parsing match data for {rank} rank in {region} region')
    

    def setupChampionDataParser(self):
        matchDataFolder = self.matchDataPath+self.patch+'/'
        champDataFolder = self.championDataPath+self.patch+'/'
        for region in self.regions:
            for rank in self.ranks:
                self.parseData(matchDataFolder, champDataFolder, region, rank)
    
    def run(self):
        if not self.checkDbs():
            self.initializeDbs()
        # self.createTestDataset()
        self.setupChampionDataParser()
        # self.writeToTestDatasetDb()
    
    def pullChampionData(self, mode):
        dbFile = self.championDataPath+self.patch+'/'+mode+'.db'
        data = []
        with sql.connect(dbFile) as db:
            c = db.cursor()
            for champ in self.champions:
                execute_string = f'SELECT * from {champ};'
                rows = c.execute(execute_string)
                data.append(lc.ChampionWinLoss(champ, rows))
        for dataPoint in data:
            print(dataPoint)
    
    def matchupPredictor(self, blueTeams, redTeams):
        dbPath = self.championDataPath+self.patch+'/'
        # for blueTeam,redTeam in zip(blueTeams,redTeams):
        #     for blue,red in zip(blueTeam,redTeam):
        #         if blue not in self.champions:
        #             print(f'ERROR! {blue} is incorrect name')
        #         if red not in self.champions:
        #             print(f'ERROR! {red} is incorrect name')
        redTeam = ['Darius', 'Graves', 'Sylas', 'Seraphine', 'Alistar']
        blueTeam = ['Renekton', 'Viego', 'Taliyah', 'Sivir', 'Yuumi']
        predictor = lc.MatchUpPredictor(dbPath, blueTeam, redTeam)
        predictor.getMatchupData()
        print(predictor)
    
    
    
    # def threadedChampionDataParser(self, matchFolder:str, champFolder:str, region:str):
    #     for rank in self.ranks:
    #         self.parseData(matchFolder, champFolder, region, rank)
    #     # threads = list()
    #     # for rank in self.ranks:
    #     #     t = Thread(target=self.parseData, args=(matchFolder, champFolder, region, rank))
    #     #     threads.append(t)
    #     #     t.start()
    #     # for t in threads:
    #     #     t.join()