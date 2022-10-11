from dataclasses import dataclass
from mimetypes import init
from nis import match
from typing import List, Dict
import sqlite3 as sql


@dataclass
class Player:
    champion: str = ''
    summoner: str = ''
    role: str = ''
    win: bool = False

    def __repr__(self) -> str:
        return f'Position: {self.role}\n         Champion: {self.champion}\n         Summoner: {self.summoner}\n          Winner?: {self.win}'


class NameTranslator:
    def __init__(self) -> None:
        self.names = {'Aatrox': 'Aatrox','Ahri': 'Ahri','Akali': 'Akali','Akshan': 'Akshan','Alistar': 'Alistar','Amumu': 'Amumu','Anivia': 'Anivia','Annie': 'Annie','Aphelios': 'Aphelios','Ashe': 'Ashe','AurelionSol': 'Aurelion Sol','Azir': 'Azir','Bard': 'Bard','Belveth': 'Bel\'Veth','Blitzcrank': 'Blitzcrank','Brand': 'Brand','Braum': 'Braum','Caitlyn': 'Caitlyn','Camille': 'Camille','Cassiopeia': 'Cassiopeia','Chogath': 'Cho\'Gath','Corki': 'Corki','Darius': 'Darius','Diana': 'Diana','DrMundo': 'Dr. Mundo','Draven': 'Draven','Ekko': 'Ekko','Elise': 'Elise','Evelynn': 'Evelynn','Ezreal': 'Ezreal','Fiddlesticks': 'Fiddlesticks','Fiora': 'Fiora','Fizz': 'Fizz','Galio': 'Galio','Gangplank': 'Gangplank','Garen': 'Garen','Gnar': 'Gnar','Gragas': 'Gragas','Graves': 'Graves','Gwen': 'Gwen','Hecarim': 'Hecarim','Heimerdinger': 'Heimerdinger','Illaoi': 'Illaoi','Irelia': 'Irelia','Ivern': 'Ivern','Janna': 'Janna','JarvanIV': 'Jarvan IV','Jax': 'Jax','Jayce': 'Jayce','Jhin': 'Jhin','Jinx': 'Jinx','Kaisa': 'Kai\'Sa','Kalista': 'Kalista','Karma': 'Karma','Karthus': 'Karthus','Kassadin': 'Kassadin','Katarina': 'Katarina','Kayle': 'Kayle','Kayn': 'Kayn','Kennen': 'Kennen','Khazix': 'Kha\'Zix','Kindred': 'Kindred','Kled': 'Kled','KogMaw': 'Kog\'Maw','Leblanc': 'LeBlanc','LeeSin': 'Lee Sin','Leona': 'Leona','Lillia': 'Lillia','Lissandra': 'Lissandra','Lucian': 'Lucian','Lulu': 'Lulu','Lux': 'Lux','Malphite': 'Malphite','Malzahar': 'Malzahar','Maokai': 'Maokai','MasterYi': 'Master Yi','MissFortune': 'Miss Fortune','MonkeyKing': 'Wukong','Mordekaiser': 'Mordekaiser','Morgana': 'Morgana','Nami': 'Nami','Nasus': 'Nasus','Nautilus': 'Nautilus','Neeko': 'Neeko','Nidalee': 'Nidalee','Nilah': 'Nilah','Nocturne': 'Nocturne','Nunu': 'Nunu & Willump','Olaf': 'Olaf','Orianna': 'Orianna','Ornn': 'Ornn','Pantheon': 'Pantheon','Poppy': 'Poppy','Pyke': 'Pyke','Qiyana': 'Qiyana','Quinn': 'Quinn','Rakan': 'Rakan','Rammus': 'Rammus','RekSai': 'Rek\'Sai','Rell': 'Rell','Renata': 'Renata Glasc','Renekton': 'Renekton','Rengar': 'Rengar','Riven': 'Riven','Rumble': 'Rumble','Ryze': 'Ryze','Samira': 'Samira','Sejuani': 'Sejuani','Senna': 'Senna','Seraphine': 'Seraphine','Sett': 'Sett','Shaco': 'Shaco','Shen': 'Shen','Shyvana': 'Shyvana','Singed': 'Singed','Sion': 'Sion','Sivir': 'Sivir','Skarner': 'Skarner','Sona': 'Sona','Soraka': 'Soraka','Swain': 'Swain','Sylas': 'Sylas','Syndra': 'Syndra','TahmKench': 'Tahm Kench','Taliyah': 'Taliyah','Talon': 'Talon','Taric': 'Taric','Teemo': 'Teemo','Thresh': 'Thresh','Tristana': 'Tristana','Trundle': 'Trundle','Tryndamere': 'Tryndamere','TwistedFate': 'Twisted Fate','Twitch': 'Twitch','Udyr': 'Udyr','Urgot': 'Urgot','Varus': 'Varus','Vayne': 'Vayne','Veigar': 'Veigar','Velkoz': 'Vel\'Koz','Vex': 'Vex','Vi': 'Vi','Viego': 'Viego','Viktor': 'Viktor','Vladimir': 'Vladimir','Volibear': 'Volibear','Warwick': 'Warwick','Xayah': 'Xayah','Xerath': 'Xerath','XinZhao': 'Xin Zhao','Yasuo': 'Yasuo','Yone': 'Yone','Yorick': 'Yorick','Yuumi': 'Yuumi','Zac': 'Zac','Zed': 'Zed','Zeri': 'Zeri','Ziggs': 'Ziggs','Zilean': 'Zilean','Zoe': 'Zoe','Zyra': 'Zyra'}
        self.nameToHex = {'Aatrox': '00', 'Ahri': '01', 'Akali': '02', 'Akshan': '03', 'Alistar': '04', 'Amumu': '05', 'Anivia': '06', 'Annie': '07', 'Aphelios': '08', 'Ashe': '09', 'AurelionSol': '0a', 'Azir': '0b', 'Bard': '0c', 'Belveth': '0d', 'Blitzcrank': '0e', 'Brand': '0f', 'Braum': '10', 'Caitlyn': '11', 'Camille': '12', 'Cassiopeia': '13', 'Chogath': '14', 'Corki': '15', 'Darius': '16', 'Diana': '17', 'Draven': '18', 'DrMundo': '19', 'Ekko': '1a', 'Elise': '1b', 'Evelynn': '1c', 'Ezreal': '1d', 'Fiddlesticks': '1e', 'Fiora': '1f', 'Fizz': '20', 'Galio': '21', 'Gangplank': '22', 'Garen': '23', 'Gnar': '24', 'Gragas': '25', 'Graves': '26', 'Gwen': '27', 'Hecarim': '28', 'Heimerdinger': '29', 'Illaoi': '2a', 'Irelia': '2b', 'Ivern': '2c', 'Janna': '2d', 'JarvanIV': '2e', 'Jax': '2f', 'Jayce': '30', 'Jhin': '31', 'Jinx': '32', 'Kaisa': '33', 'Kalista': '34', 'Karma': '35', 'Karthus': '36', 'Kassadin': '37', 'Katarina': '38', 'Kayle': '39', 'Kayn': '3a', 'Kennen': '3b', 'Khazix': '3c', 'Kindred': '3d', 'Kled': '3e', 'KogMaw': '3f', 'Leblanc': '40', 'LeeSin': '41', 'Leona': '42', 'Lillia': '43', 'Lissandra': '44', 'Lucian': '45', 'Lulu': '46', 'Lux': '47', 'Malphite': '48', 'Malzahar': '49', 'Maokai': '4a', 'MasterYi': '4b', 'MissFortune': '4c', 'MonkeyKing': '4d', 'Mordekaiser': '4e', 'Morgana': '4f', 'Nami': '50', 'Nasus': '51', 'Nautilus': '52', 'Neeko': '53', 'Nidalee': '54', 'Nilah': '55', 'Nocturne': '56', 'Nunu': '57', 'Olaf': '58', 'Orianna': '59', 'Ornn': '5a', 'Pantheon': '5b', 'Poppy': '5c', 'Pyke': '5d', 'Qiyana': '5e', 'Quinn': '5f', 'Rakan': '60', 'Rammus': '61', 'RekSai': '62', 'Rell': '63', 'Renata': '64', 'Renekton': '65', 'Rengar': '66', 'Riven': '67', 'Rumble': '68', 'Ryze': '69', 'Samira': '6a', 'Sejuani': '6b', 'Senna': '6c', 'Seraphine': '6d', 'Sett': '6e', 'Shaco': '6f', 'Shen': '70', 'Shyvana': '71', 'Singed': '72', 'Sion': '73', 'Sivir': '74', 'Skarner': '75', 'Sona': '76', 'Soraka': '77', 'Swain': '78', 'Sylas': '79', 'Syndra': '7a', 'TahmKench': '7b', 'Taliyah': '7c', 'Talon': '7d', 'Taric': '7e', 'Teemo': '7f', 'Thresh': '80', 'Tristana': '81', 'Trundle': '82', 'Tryndamere': '83', 'TwistedFate': '84', 'Twitch': '85', 'Udyr': '86', 'Urgot': '87', 'Varus': '88', 'Vayne': '89', 'Veigar': '8a', 'Velkoz': '8b', 'Vex': '8c', 'Vi': '8d', 'Viego': '8e', 'Viktor': '8f', 'Vladimir': '90', 'Volibear': '91', 'Warwick': '92', 'Xayah': '93', 'Xerath': '94', 'XinZhao': '95', 'Yasuo': '96', 'Yone': '97', 'Yorick': '98', 'Yuumi': '99', 'Zac': '9a', 'Zed': '9b', 'Zeri': '9c', 'Ziggs': '9d', 'Zilean': '9e', 'Zoe': '9f', 'Zyra': 'a0'}
        self.hexToName = {'00': 'Aatrox', '01': 'Ahri', '02': 'Akali', '03': 'Akshan', '04': 'Alistar', '05': 'Amumu', '06': 'Anivia', '07': 'Annie', '08': 'Aphelios', '09': 'Ashe', '0a': 'AurelionSol', '0b': 'Azir', '0c': 'Bard', '0d': 'Belveth', '0e': 'Blitzcrank', '0f': 'Brand', '10': 'Braum', '11': 'Caitlyn', '12': 'Camille', '13': 'Cassiopeia', '14': 'Chogath', '15': 'Corki', '16': 'Darius', '17': 'Diana', '18': 'Draven', '19': 'DrMundo', '1a': 'Ekko', '1b': 'Elise', '1c': 'Evelynn', '1d': 'Ezreal', '1e': 'Fiddlesticks', '1f': 'Fiora', '20': 'Fizz', '21': 'Galio', '22': 'Gangplank', '23': 'Garen', '24': 'Gnar', '25': 'Gragas', '26': 'Graves', '27': 'Gwen', '28': 'Hecarim', '29': 'Heimerdinger', '2a': 'Illaoi', '2b': 'Irelia', '2c': 'Ivern', '2d': 'Janna', '2e': 'JarvanIV', '2f': 'Jax', '30': 'Jayce', '31': 'Jhin', '32': 'Jinx', '33': 'Kaisa', '34': 'Kalista', '35': 'Karma', '36': 'Karthus', '37': 'Kassadin', '38': 'Katarina', '39': 'Kayle', '3a': 'Kayn', '3b': 'Kennen', '3c': 'Khazix', '3d': 'Kindred', '3e': 'Kled', '3f': 'KogMaw', '40': 'Leblanc', '41': 'LeeSin', '42': 'Leona', '43': 'Lillia', '44': 'Lissandra', '45': 'Lucian', '46': 'Lulu', '47': 'Lux', '48': 'Malphite', '49': 'Malzahar', '4a': 'Maokai', '4b': 'MasterYi', '4c': 'MissFortune', '4d': 'MonkeyKing', '4e': 'Mordekaiser', '4f': 'Morgana', '50': 'Nami', '51': 'Nasus', '52': 'Nautilus', '53': 'Neeko', '54': 'Nidalee', '55': 'Nilah', '56': 'Nocturne', '57': 'Nunu', '58': 'Olaf', '59': 'Orianna', '5a': 'Ornn', '5b': 'Pantheon', '5c': 'Poppy', '5d': 'Pyke', '5e': 'Qiyana', '5f': 'Quinn', '60': 'Rakan', '61': 'Rammus', '62': 'RekSai', '63': 'Rell', '64': 'Renata', '65': 'Renekton', '66': 'Rengar', '67': 'Riven', '68': 'Rumble', '69': 'Ryze', '6a': 'Samira', '6b': 'Sejuani', '6c': 'Senna', '6d': 'Seraphine', '6e': 'Sett', '6f': 'Shaco', '70': 'Shen', '71': 'Shyvana', '72': 'Singed', '73': 'Sion', '74': 'Sivir', '75': 'Skarner', '76': 'Sona', '77': 'Soraka', '78': 'Swain', '79': 'Sylas', '7a': 'Syndra', '7b': 'TahmKench', '7c': 'Taliyah', '7d': 'Talon', '7e': 'Taric', '7f': 'Teemo', '80': 'Thresh', '81': 'Tristana', '82': 'Trundle', '83': 'Tryndamere', '84': 'TwistedFate', '85': 'Twitch', '86': 'Udyr', '87': 'Urgot', '88': 'Varus', '89': 'Vayne', '8a': 'Veigar', '8b': 'Velkoz', '8c': 'Vex', '8d': 'Vi', '8e': 'Viego', '8f': 'Viktor', '90': 'Vladimir', '91': 'Volibear', '92': 'Warwick', '93': 'Xayah', '94': 'Xerath', '95': 'XinZhao', '96': 'Yasuo', '97': 'Yone', '98': 'Yorick', '99': 'Yuumi', '9a': 'Zac', '9b': 'Zed', '9c': 'Zeri', '9d': 'Ziggs', '9e': 'Zilean', '9f': 'Zoe', 'a0': 'Zyra'}
    
    def getHexFromName(self, name):
        if name not in self.nameToHex.keys():
            raise ValueError("Incorrect champion name given for hex translation")
        return self.nameToHex[name]

    def getNameFromHex(self, hexCode):
        if hexCode not in self.hexToName.keys():
            raise ValueError("Incorrect hex given for champion name translation")
        return self.hexToName[hexCode]
    
    def generateMatchHexString(self, match):
        hexString = ''

        winner = match[2]
        winnerHex = ''
        if winner == 'red':
            winnerHex = f'{238:02x}'
        elif winner == 'blue':
            winnerHex = f'{255:02x}'
        hexString += winnerHex
        
        redTeam = match[3:8]
        redHexes = [self.getHexFromName(r) for r in redTeam]
        for redHex in redHexes:
            hexString += redHex
        
        blueTeam = match[8:13]
        blueHexes = [self.getHexFromName(b) for b in blueTeam]
        for blueHex in blueHexes:
            hexString += blueHex
        
        return hexString
    
    def getTeamsFromHexString(self, hexString):
        redTeam = []
        blueTeam = []
        if len(hexString) == 22:
            redTeam = hexString[2:12]
            blueTeam = hexString[12:22]
        elif len(hexString) == 20:
            redTeam = hexString[:10]
            blueTeam = hexString[10:20]
        teams = ['' for _ in range(10)]
        j = 0
        for i in range(0, 10, 2):
            teams[j] = self.getNameFromHex(redTeam[i:i+2])
            teams[j+5] = self.getNameFromHex(blueTeam[i:i+2])
            j+=1
        return teams
    
    def getIndividualTeamFromHexString(self, hexString):
        names = ['' for _ in range(5)]
        j = 0
        for i in range(0, 10, 2):
            names[j] = self.getNameFromHex(hexString[i:i+2])
            j+=1
        return names

    def forward(self, name):
        if name not in self.names.keys():
            raise ValueError("Incorrect champion name given for forward lookup")
        return self.names[name]
    
    def reverse(self, name):
        if name not in self.names.values():
            raise ValueError("Incorrect champion name given for reverse lookup")
        for key,value in self.names.items():
            if name == value:
                return key
    
    def getList(self):
        return self.names


class Team:
    def __init__(self, side) -> None:
        self.players = [Player() for _ in range(5)]
        self.side = side
        self.role = {
            'TOP': 0,
            'JUNGLE': 1,
            'MIDDLE': 2,
            'BOTTOM': 3,
            'UTILITY': 4,
            '': 4
        }

    def __str__(self) -> str:
        return f'####{self.side} side####\n    Top: {self.players[0]}\n\n Jungle: {self.players[1]}\n\n Middle: {self.players[2]}\n\n Bottom: {self.players[3]}\n\nSupport: {self.players[4]}\n'

    def add_player(self, champ: str, name: str, position: str, win: bool):
        if champ == 'FiddleSticks':
            champ = champ.title()
        self.players[self.role[position]] = Player(
            champion=champ, summoner=name, role=position, win=win)


class MatchInfo:
    def __init__(self, match_data) -> None:
        self.blue, self.red, self.winner, self.gameID = self.parse_match(
            match_data)

    def __str__(self) -> str:
        return f'#### - Match Data - ####\nID number: {self.gameID}\n{self.blue}\n{self.red}\nWinner: {self.winner}'

    def parse_match(self, match_data):
        red_team = Team('red')
        blue_team = Team('blue')
        game_id = match_data['info']['gameId']
        for gamer in match_data["info"]["participants"]:
            if gamer['teamId'] == 200:
                red_team.add_player(
                    gamer['championName'], gamer['summonerName'], gamer['teamPosition'], gamer['win'])
                if gamer['win'] == True:
                    winner = 'red'
            if gamer['teamId'] == 100:
                blue_team.add_player(
                    gamer['championName'], gamer['summonerName'], gamer['teamPosition'], gamer['win'])
                if gamer['win'] == True:
                    winner = 'blue'
        return blue_team, red_team, winner, game_id

    def convert_to_db_tuple(self):
        data = (self.gameID,
                self.winner,
                self.red.players[0].champion,
                self.red.players[1].champion,
                self.red.players[2].champion,
                self.red.players[3].champion,
                self.red.players[4].champion,
                self.blue.players[0].champion,
                self.blue.players[1].champion,
                self.blue.players[2].champion,
                self.blue.players[3].champion,
                self.blue.players[4].champion)
        return data

# @dataclass
# class WinLoss:


class ChampionWinLoss:
    def __init__(self, name: str, data: list()) -> None:
        self.champion = name
        #            wins  ,  losses
        self.KR = [[0, 0, 0], [0, 0, 0]]
        self.NA = [[0, 0, 0], [0, 0, 0]]
        self.EUN = [[0, 0, 0], [0, 0, 0]]
        self.EUW = [[0, 0, 0], [0, 0, 0]]
        for row in data:
            # Korea wins
            self.KR[0][0] += row[1]
            self.KR[0][1] += row[3]
            self.KR[0][2] += row[5]
            # Korea losses
            self.KR[1][0] += row[2]
            self.KR[1][1] += row[4]
            self.KR[1][2] += row[6]

            # North America wins
            self.NA[0][0] += row[7]
            self.NA[0][1] += row[9]
            self.NA[0][2] += row[11]
            # North America losses
            self.NA[1][0] += row[8]
            self.NA[1][1] += row[10]
            self.NA[1][2] += row[12]

            # Europe North wins
            self.EUN[0][0] += row[13]
            self.EUN[0][1] += row[15]
            self.EUN[0][2] += row[17]
            # Europe North losses
            self.EUN[1][0] += row[14]
            self.EUN[1][1] += row[16]
            self.EUN[1][2] += row[18]

            # Europe West wins
            self.EUW[0][0] += row[19]
            self.EUW[0][1] += row[21]
            self.EUW[0][2] += row[23]
            # Europe West losses
            self.EUW[1][0] += row[20]
            self.EUW[1][1] += row[22]
            self.EUW[1][2] += row[24]

    def getTotalWins(self):
        krWins = sum(self.KR[0])
        naWins = sum(self.NA[0])
        euWins = sum(self.EUN[0]) + sum(self.EUW[0])
        return (krWins + naWins + euWins)

    def getTotalLosses(self):
        krLosses = sum(self.KR[1])
        naLosses = sum(self.NA[1])
        euLosses = (sum(self.EUN[1]) + sum(self.EUW[1]))
        return (krLosses + naLosses + euLosses)

    def getWinsByRegion(self, region: str):
        if 'NA' in region:
            return sum(self.NA[0])
        elif 'KR' in region:
            return sum(self.KR[0])
        elif 'EUW' in region:
            return sum(self.EUW[0])
        elif 'EUN' in region:
            return sum(self.EUN[0])
        elif 'EU' in region:
            return sum(sum(self.EUN[0]), sum(self.EUW[0]))
        else:
            print('ERROR, incorrect region given')

    def getLossesByRegion(self, region: str):
        if 'NA' in region:
            return sum(self.NA[1])
        elif 'KR' in region:
            return sum(self.KR[1])
        elif 'EUW' in region:
            return sum(self.EUW[1])
        elif 'EUN' in region:
            return sum(self.EUN[1])
        elif 'EU' in region:
            return sum(sum(self.EUN[1]), sum(self.EUW[1]))
        else:
            print('ERROR, incorrect region given')

    def getWinPercentage(self):
        wins = self.getTotalWins()
        losses = self.getTotalLosses()
        total = wins + losses
        if total == 0:
            winp = 0
        else:
            winP = wins / total
        return round(winP*100.0, 2)

    def getWinPercentByRegion(self, region):
        wins = self.getWinsByRegion(region)
        losses = self.getLossesByRegion(region)
        total = wins+losses
        if total == 0:
            winP = 0
        else:
            winP = wins / total
        return round(winP*100.0, 2)

    def __repr__(self) -> str:
        s = f'''
        |======================================================================|
        |{self.champion:^70}|
        |----------------------------------------------------------------------|
        |  Team |        wins        |       losses       |        Win%        |
        |-------|--------------------|--------------------|--------------------|
        |   KR  |{self.getWinsByRegion('KR'):^20}|{self.getLossesByRegion('KR'):^20}|{self.getWinPercentByRegion('KR'):^20.2f}|
        |   NA  |{self.getWinsByRegion('NA'):^20}|{self.getLossesByRegion('NA'):^20}|{self.getWinPercentByRegion('NA'):^20.2f}|
        |  EUW  |{self.getWinsByRegion('EUW'):^20}|{self.getLossesByRegion('EUW'):^20}|{self.getWinPercentByRegion('EUW'):^20.2f}|
        |  EUN  |{self.getWinsByRegion('EUN'):^20}|{self.getLossesByRegion('EUN'):^20}|{self.getWinPercentByRegion('EUN'):^20.2f}|
        | Total |{self.getTotalWins():^20}|{self.getTotalLosses():^20}|{self.getWinPercentage():^20.2f}|
        |======================================================================|'''
        return s


class MatchUpPredictor:
    def __init__(self, dbFolderPath: str, blue_team: List[str], red_team: List[str]) -> None:
        self.versusPath = dbFolderPath+'versus.db'
        self.alliedPath = dbFolderPath+'allied.db'
        self.blueTeam = blue_team
        self.redTeam = red_team
        self.redVersus = [0 for _ in range(5)]
        self.redVersusTotal = 0
        self.blueVersus = [0 for _ in range(5)]
        self.blueVersusTotal = 0
        self.redAlly = [0 for _ in range(5)]
        self.redAlliedTotal = 0
        self.blueAlly = [0 for _ in range(5)]
        self.blueAlliedTotal = 0
        self.redVersusEdge = [0 for _ in range(5)]
        self.redAlliedEdge = [0 for _ in range(5)]
        self.blueVersusEdge = [0 for _ in range(5)]
        self.blueAlliedEdge = [0 for _ in range(5)]
        self.redTotalEdge = 0
        self.blueTotalEdge = 0
        self.prediction = ''

    def pullFromDatabase(self, champ1: str, champ2: str, c, mode: str):
        execute_string = f'SELECT * from {champ1} WHERE {mode} = ?;'
        execute_data = (champ2,)
        row = c.execute(execute_string, execute_data).fetchall()
        winLoss = ChampionWinLoss(champ1, row)
        # print(winLoss)
        return winLoss.getWinPercentage()

    def getMatchupData(self):
        with sql.connect(self.versusPath) as db:
            c = db.cursor()
            for i, red in enumerate(self.redTeam):
                for blue in self.blueTeam:
                    self.redVersus[i] += self.pullFromDatabase(
                        red, blue, c, 'versus')
                self.redVersus[i] = round((self.redVersus[i]/5.0), 2)
            self.redVersusTotal = round(sum(self.redVersus)/5.0, 2)
            for j, blue in enumerate(self.blueTeam):
                for red in self.redTeam:
                    self.blueVersus[j] += self.pullFromDatabase(
                        blue, red, c, 'versus')
                self.blueVersus[j] = round((self.blueVersus[j]/5.0), 2)
            self.blueVersusTotal = round(sum(self.blueVersus)/5.0, 2)

        with sql.connect(self.alliedPath) as db:
            c = db.cursor()
            for m, red in enumerate(self.redTeam):
                for ally in self.redTeam:
                    if red != ally:
                        self.redAlly[m] += self.pullFromDatabase(
                            red, ally, c, 'allied')
                self.redAlly[m] = round((self.redAlly[m]/4.0), 2)
            self.redAlliedTotal = round(sum(self.redAlly)/5.0, 2)
            for n, blue in enumerate(self.blueTeam):
                for ally in self.blueTeam:
                    if blue != ally:
                        self.blueAlly[n] += self.pullFromDatabase(
                            blue, ally, c, 'allied')
                self.blueAlly[n] = round((self.blueAlly[n]/4.0), 2)
            self.blueAlliedTotal = round(sum(self.blueAlly)/5.0, 2)

        for i in range(5):
            if self.redVersus[i] > self.blueVersus[i]:
                self.redVersusEdge[i] = 1
            else:
                self.blueVersusEdge[i] = 1
            if self.redAlly[i] > self.blueAlly[i]:
                self.redAlliedEdge[i] = 1
            else:
                self.blueAlliedEdge[i] = 1
        self.redTotalEdge = sum(self.redVersusEdge) + sum(self.redAlliedEdge)
        self.blueTotalEdge = sum(self.blueVersusEdge) + \
            sum(self.blueAlliedEdge)
        if self.redTotalEdge > self.blueTotalEdge:
            self.prediction = 'red'
        elif self.blueTotalEdge > self.redTotalEdge:
            self.prediction = 'blue'
        else:
            self.prediction = 'too close'

    def __repr__(self) -> str:
        title = 'Blue | vs | Red'
        s = f'''
        |====================================================================|
        |{title:^68}|
        |--------------------------------------------------------------------|
        |{'Champion':^20}|{'versus':^10}| vs |{'versus':^10}|{'Champion':^20}|
        |                    |{'allied':^10}| vs |{'allied':^10}|                    |
        |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
        |{self.blueTeam[0]:^20}|{self.blueVersus[0]:^10}| vs |{self.redVersus[0]:^10}|{self.redTeam[0]:^20}|
        |                    |{self.blueAlly[0]:^10}|    |{self.redAlly[0]:^10}|                    |
        |--------------------------------------------------------------------|
        |{self.blueTeam[1]:^20}|{self.blueVersus[1]:^10}| vs |{self.redVersus[1]:^10}|{self.redTeam[1]:^20}|
        |                    |{self.blueAlly[1]:^10}|    |{self.redAlly[1]:^10}|                    |
        |--------------------------------------------------------------------|
        |{self.blueTeam[2]:^20}|{self.blueVersus[2]:^10}| vs |{self.redVersus[2]:^10}|{self.redTeam[2]:^20}|
        |                    |{self.blueAlly[2]:^10}|    |{self.redAlly[2]:^10}|                    |
        |--------------------------------------------------------------------|
        |{self.blueTeam[3]:^20}|{self.blueVersus[3]:^10}| vs |{self.redVersus[3]:^10}|{self.redTeam[3]:^20}|
        |                    |{self.blueAlly[3]:^10}|    |{self.redAlly[3]:^10}|                    |
        |--------------------------------------------------------------------|
        |{self.blueTeam[4]:^20}|{self.blueVersus[4]:^10}| vs |{self.redVersus[4]:^10}|{self.redTeam[4]:^20}|
        |                    |{self.blueAlly[4]:^10}|    |{self.redAlly[4]:^10}|                    |
        |====================================================================|
        |{'Total':^20}|{self.blueVersusTotal:^10}| vs |{self.redVersusTotal:^10}|{'Total':^20}|
        |                    |{self.blueAlliedTotal:^10}|    |{self.redAlliedTotal:^10}|                    |
        |--------------------------------------------------------------------|
        |   prediction : {self.prediction:<52}|
        |====================================================================|
        '''
        return s
