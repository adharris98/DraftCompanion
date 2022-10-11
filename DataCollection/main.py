from riotwatcher import LolWatcher, ApiError
import sqlite3 as sql
from pprint import pprint as pp
import json
import pyinputplus as pyip
from riotData import Riot
from userClass import User
from summonerGrabber import SummonerGrabber
from matchIDGrabber import MatchIDGrabber
from parseMatches import MatchParser
from championData import ChampionDataParser
from datetime import datetime
import csv


# eventually turn this into an app that makes the process easy to execute

# the data collection process is:
# 1. gather the names of the players currently in the top three divisions (Challenger, Grandmaster, Master)
# 2. get the matchids of games played by these players during the given patch
# 3. parse the matches and collect champion specific data from the matches
# 4. handle the champion data and calculate important relationships

# the databases will need to be separated by patch
# player names, match ids, and champion data

def main():
    # initialize all the classes that are needed
    riot = Riot()
    user = User('na1', 'AMERICAS', '5pa6es')
    watcher = user.getWatcher()

    # collectedPatches = []
    # with open('dataCollectedFor.txt') as f:
    #     lines = f.readlines()
    #     for line in lines:
    #         collectedPatches.append(line.strip('\n'))
    # patch = pyip.inputChoice(riot.getVersions(watcher.data_dragon), prompt='Enter the desired patch: ', blockRegexes=collectedPatches)
    patch = 'patch_12_18'
    regions = riot.getRegions()
    continents = riot.getContinents()
    ranks = riot.getRanks()
    queueType = riot.getQueueType()
    queueId = riot.getQueueID()
    champNames = riot.getChampionNames(watcher, patch)
    start = datetime(2022,9,22)

    # now initialize all the data grabbers
    # Summoner Grabber
    # sg = SummonerGrabber(regions=regions, ranks=ranks, queueType=queueType, watcher=watcher, patch=patch)
    # Match ID Grabber
    mg = MatchIDGrabber(regions=regions, continents=continents, ranks=ranks, queueID=queueId, watcher=watcher, patch=patch, startDate=start)
    # Match Parser
    mp = MatchParser(regions=regions, continents=continents, ranks=ranks, watcher=watcher, patch=patch)
    # Champion Data Parser
    cdp = ChampionDataParser(regions=regions, ranks=ranks, patch=patch, champNames=champNames)

    # print(f'Gathering summoners from high elo for patch {patch}...')
    # sg.run()
    # print()
    # print(f'Gathering match Ids from high elo players...')
    # mg.run()
    # print()
    # print(f'Parsing high elo matches...')
    # mp.run()
    # print()
    # print(f'Parsing collected champion data')
    # cdp.run()
    # print()
    # cdp.pullChampionData('versus')
    blueTeams = []
    redTeams = []
    with open('/Users/adamharris/Documents/DraftCompanion/DataCollection/worldsPicks2022.csv', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if '' not in row:
                # print(row[:5], row[5:])
                blueTeams.append(row[:5])
                redTeams.append(row[5:])
    cdp.matchupPredictor(blueTeams, redTeams)

if __name__ == "__main__":
    main()