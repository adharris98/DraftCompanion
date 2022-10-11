from nis import match
import sqlite3 as sql
import sys
sys.path.append('..')
from riotData import Riot
from userClass import User
import LoLClasses as lc
import csv
from pprint import pprint as pp

def extractMatchData(filepath, rank, region):
    with sql.connect(filepath) as db:
        c = db.cursor()
        executeString = f'SELECT * from {rank};'
        rows = c.execute(executeString).fetchall()
        cleanRows = [[region]+list(item) for item in rows if '' not in item]
    return cleanRows

def writeToCsv(dataFile, header, data, translator:lc.NameTranslator):
    with open(dataFile, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for item in data:
            writer.writerow([translator.generateMatchHexString(item)]+item)

def evaluateMatches(data, translator:lc.NameTranslator):
    matches = dict()
    for item in data:
        hexString = translator.generateMatchHexString(item)[2:]
        team1 = hexString[:10]
        team2 = hexString[10:20]
        hexString2 = team2+team1
        if hexString in matches.keys():
            matches[hexString] += 1
        else:
            matches[hexString] = 1
        if hexString2 in matches.keys():
            matches[hexString2] += 1
        else:
            matches[hexString2] = 1
    return matches

def evaluateTeamComps(data, translator):
    comps = dict()
    for item in data:
        hexString = translator.generateMatchHexString(item)
        teams = []
        teams.append(hexString[2:12])
        teams.append(hexString[12:22])
        for team in teams:
            if team in comps.keys():
                comps[team] += 1
            else:
                comps[team] = 1
    return comps

def compigami(data, translator:lc.NameTranslator):
    matches = evaluateMatches(data, translator)
    for key,value in matches.items():
        if value >= 2:
            print(key)
    print('Finished with match evaluation')

    comps = evaluateTeamComps(data, translator)
    for key,value in comps.items():
        if value >= 2:
            print(f'{translator.getIndividualTeamFromHexString(key)} : {value}')
    print('Finished with comps evaluation')

def writeNumbersToCsv(dataFile, header, data, translator:lc.NameTranslator):
    with open(dataFile, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for item in data:
            # print(item[2:])
            for i in range(3,len(item)):
                item[i] = int('0x'+translator.getHexFromName(item[i]), base=16)
            # print(item[2:])
            writer.writerow(item[2:])

def main():
    riot = Riot()
    # user = User('na1', 'AMERICAS', '5pa6es')
    # watcher = user.getWatcher()
    translator = lc.NameTranslator()
    matchDataFilepath = '/Users/adamharris/Documents/DraftCompanion/DataCollection/matchData/patch_12_18/'
    header = ['hexcode', 'region', 'match_id', 'winner', 'red_top', 'red_jungle', 'red_mid', 'red_adc', 'red_support', 'blue_top', 'blue_jungle', 'blue_mid', 'blue_adc', 'blue_support']
    numberHeader = ['winner', 'red_top', 'red_jungle', 'red_mid', 'red_adc', 'red_support', 'blue_top', 'blue_jungle', 'blue_mid', 'blue_adc', 'blue_support']
    dataFile = '/Users/adamharris/Documents/DraftCompanion/DataCollection/LogisticalRegression/matchData.csv'
    numberedFile = '/Users/adamharris/Documents/DraftCompanion/DataCollection/LogisticalRegression/matchDataNumbered.csv'
    matchData = list()
    for region in riot.getRegions():
        for rank in riot.getRanks():
            filepath = matchDataFilepath+region+'.db'
            matchData += extractMatchData(filepath, rank, region)
    writeToCsv(dataFile, header, data=matchData, translator=translator)
    # compigami(data=matchData, translator=translator)
    writeNumbersToCsv(numberedFile, numberHeader, data=matchData, translator=translator)

    

if __name__ == "__main__":
    main()