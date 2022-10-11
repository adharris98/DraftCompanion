from turtle import forward
from riotwatcher import LolWatcher
from riotData import Riot
from userClass import User
from summonerGrabber import SummonerGrabber
from matchIDGrabber import MatchIDGrabber
from parseMatches import MatchParser
from championData import ChampionDataParser
from pprint import pprint as pp
import json
from datetime import datetime
import LoLClasses as lc


def testSummonerGrabber(riot, watcher, patch):
    print('Testing initialization')
    sg = SummonerGrabber(riot.getRegions(), riot.getRanks(), riot.getQueueType(), watcher, patch)
    print('passed\n')
    
    if not sg.checkDbs():
        print('Testing db initialization')
        sg.initializeDbs()
        print('passed\n')
    
    print('Testing the name getter function')
    sg.getSummonerNames()
    print('passed\n')

    print('Testing ID getter function')
    with open('/Users/adamharris/Documents/DraftCompanion/DataCollection/testDict.json') as f:
        highEloTest = json.load(f)
    sg.getIDsTest(highEloTest)
    print('passed\n')

def testMatchIDGrabber(riot, watcher, patch):
    print('Testing initialization')
    mg = MatchIDGrabber(riot.getRegions(), riot.getContinents(), riot.getRanks(), riot.getQueueID(), watcher, patch, datetime(2022,9,22))
    print('passed\n')
    
    if not mg.checkDbs():
        print('Testing db initialization')
        mg.initializeDbs()
        print('passed\n')
    
    print('Testing matchGetter')
    mg.setupMatchGetter()
    print('passed\n')

def testMatchParser(indent, riot, watcher, patch):
    print(indent+'Testing initialization\n')
    mp = MatchParser(riot.getRegions(), riot.getContinents(), riot.getRanks(), watcher, patch)
    print(indent+'passed\n')

    if not mp.checkDbs():
        print(indent+'Testing db initialization\n')
        mp.initializeDbs()
        print(indent+'passed\n')
    
    print(indent+'Testing Match Parser\n')
    mp.setupMatchParser()
    print(indent+'passed\n')

def testChampionDataParser(riot:Riot, watcher:LolWatcher, patch):
    champNames = riot.getChampionNames(watcher, patch)
    print('Testing initialization')
    cdp = ChampionDataParser(riot.getRegions(), riot.getRanks(), patch, champNames)
    print('passed\n')

    if not cdp.checkDbs():
        print('Testing initialization')
        cdp.initializeDbs()
        print('passed\n')

    print('Testing Champion Data Parser')
    cdp.setupChampionDataParser()
    print('passed\n')

def createChampionNameTranslatorDictionary(riot:Riot, watcher:LolWatcher):
    champions = riot.getChampionNames(watcher, 'patch_12_18')
    translator = dict()
    for i,name in enumerate(champions):
        # h = hex(i)
        translator[f'{i:02x}'] = name
    print(translator)

# This file is used to test all of the other functions 
def main():
    print('Testing the Riot object initialization')
    riot = Riot()
    print('passed\n')

    print('Testing the User object initialization')
    user = User('na1', 'AMERICAS', '5pa6es')
    watcher = user.getWatcher()
    print('passed\n')

    # print('Testing the Summoner Grabber')
    # testSummonerGrabber(riot, watcher, 'patch_12_18')
    # print('passed\n')

    # print('Testing the Match ID Grabber')
    # testMatchIDGrabber(riot, watcher, 'patch_12_18')
    # print('passed\n')

    # print('Testing Match Parser\n')
    # testMatchParser('   ', riot, watcher, 'patch_12_18')
    # print('passed\n')

    # print('Testing Champion Data Parser\n')
    # testChampionDataParser(riot, watcher, 'patch_12_18')
    # print('passed\n')

    createChampionNameTranslatorDictionary(riot, watcher)
    # translator = lc.NameTranslator()
    # fwd = translator.forward('MonkeyKing')
    # rvs = translator.reverse('Wukong')
    # print(f'forward: MonkeyKing => {fwd}')
    # print(f'reverse: Wukong => {rvs}')
    




if __name__ == "__main__":
    main()