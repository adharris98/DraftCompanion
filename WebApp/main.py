from crypt import methods
import os, sys
import flask
import databaseHelper as dbh
from riotwatcher import LolWatcher
from pprint import pprint as pp
import sqlite3 as sql
import lolDataFunctions as df
import lolClasses as lc

app = flask.Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    return flask.render_template("index.html")

@app.route("/champion_list", methods=['GET', 'POST'])
def champion_list():
    user = lc.User('na1', 'AMERICAS', '5pa6es')
    watcher = user.getWatcher()
    champNames = df.getChampNames(df.getChampList(watcher.data_dragon, "11.19.1"))
    print(len(champNames))
    champ_dict = {}
    champ_list = []
    champ_row = []
    count = 0
    total = 0
    # champ_images_dict = {}
    for champ in champNames:
        champ_row.append(champ)
        count = count + 1
        if count==6:
            print("inserting next row into list")
            champ_list.append(champ_row)
            champ_row = []
            total = total + count
            count = 0
        if total==156 and count!=0:
            champ_row.extend([0, 0, 0, 0, 0])
            champ_list.append(champ_row)
        print(f"count: {count}\ntotal: {total}")
        # filename = f"data/championImages/{champ}.png"
        # filename = f"/static/images/{champ}.png"
        # champ_dict.update({champ:[champ, filename]})
        # champ_images_dict.update({champ:filename})
    # for key,value in champ_images_dict.items():
        # print(champ_images_dict[key])
    for row in champ_list:
        print(row)
    return flask.render_template("champion_data.html", data = champ_list)

@app.route("/champion_data/versus/<champion>", methods=['GET', 'POST'])
def display_champion_versus_data(champion):
    champion_data = []
    headers = ['Versus', 'Wins', 'Losses', 'Win Percentage', 'Wins Above Riot (W.A.R.)']
    with sql.connect("data/champion_head_to_head.db") as db:
        c = db.cursor()
        execute_string = f"SELECT * FROM {champion};"
        rows = c.execute(execute_string).fetchall()
        for row in rows:
            versus, wins, losses, win_percentage, war_1, war_2 = row
            win_p = round(win_percentage*100.0, 2)
            war = round(war_2*100.0, 2)
            champion_data.append([versus, wins, losses, win_p, war])
    return flask.render_template("champion_h2h_stats.html", page_title=champion, table_headers=headers, data=champion_data)


# CREATE A CHAMPION STAT DISPLAY HTML FILE AND LOAD IT WITH VERSUS/ALLY DATA
#   MIGHT NEED TWO DIFFERENT HTMLS FOR VERSUS AND ALLY

@app.route("/champion_data/ally/<champion>", methods=['GET', 'POST'])
def display_champion_ally_data(champion):
    champion_data = []
    headers = ['Ally', 'Wins', 'Losses', 'Win Percentage']
    with sql.connect("data/champion_ally_stats.db") as db:
        c = db.cursor()
        execute_string = f"SELECT * FROM {champion};"
        rows = c.execute(execute_string).fetchall()
        for row in rows:
            ally, wins, losses, win_percentage = row
            win_p = round(win_percentage*100.0, 2)
            champion_data.append([ally, wins, losses, win_p])
    return flask.render_template("champion_ally_stats.html", page_title=champion, table_headers=headers, data=champion_data)

@app.route("/one_v_one", methods=['GET', 'POST'])
def one_v_one():
    user = lc.User('na1', 'AMERICAS', '5pa6es')
    watcher = user.getWatcher()
    champNames = df.getChampNames(df.getChampList(watcher.data_dragon, "11.19.1"))
    userMessage = "Select your champion"
    enemyMessage = "Select enemy champion"
    userSelect = "None"
    enemySelect = "None"
    # print(champNames)
    # if flask.request.method == 'POST':
    user_champ = flask.request.form.get('user_champion')
    enemy_champ = flask.request.form.get('enemy_champion')
    print("user champ: ", user_champ, "enemy champ: ", enemy_champ)
    display = False
    table_headers = ['Wins', 'Losses', 'Win Percentage', 'Wins Above Riot (W.A.R.)']
    rows = []
    matchupData = []
    if (user_champ in champNames) and (enemy_champ in champNames):
        display = True
        table_headers[0] = user_champ+' '+table_headers[0]
        table_headers[1] = enemy_champ+' Wins'
        userMessage = user_champ
        enemyMessage = enemy_champ
        dbFile = "data/champion_head_to_head.db"
        rows = dbh.get_matchup_data(dbFile, user_champ, enemy_champ, 'all')
        print(rows)
        for row in rows:
            versus, wins, losses, win_percentage, war1, war_2 = row
            win_p = round(win_percentage*100.0, 2)
            war = round(war_2*100.0, 2)
            matchupData.append([wins, losses, win_p, war])
    # return flask.render_template("one_v_one.html", champions=champNames, userSelectMessage=userMessage, enemySelectMessage=enemyMessage, userSelect=userSelect, enemySelect=enemySelect)
    return flask.render_template("one_v_one.html", champions=champNames, display=display, data=matchupData, table_headers=table_headers, user=user_champ, enemy=enemy_champ, userMessage=userMessage, enemyMessage=enemyMessage)

@app.route("/one_v_one/<userChamp>/<enemyChamp>", methods=['GET', 'POST'])
def one_v_one_picks(userChamp=None, enemyChamp=None):
    user = lc.User('na1', 'AMERICAS', '5pa6es')
    watcher = user.getWatcher()
    champNames = df.getChampNames(df.getChampList(watcher.data_dragon, "11.19.1"))
    userMessage = "Select your champion"
    enemyMessage = "Select enemy champion"
    userSelect = "None"
    enemySelect = "None"
    if userChamp != "None":
        userMessage = f"{userChamp}"
        userSelect = f"{userChamp}"
    if enemyChamp != "None":
        enemyMessage = f"{enemyChamp}"
        enemySelect = f"{enemyChamp}"
    # print(champNames)
    # user_champ = flask.request.form.get('user_champion')
    # enemy_champ = flask.request.form.get('enemy_champion')
    # print(user_champ, enemy_champ)
    return flask.render_template("one_v_one.html", champions=champNames, userSelectMessage=userMessage, enemySelectMessage=enemyMessage, userSelect=userSelect, enemySelect=enemySelect)
    # return f"picks: {userChamp}, {enemyChamp}"

@app.route("/five_v_five", methods=['GET', 'POST'])
def five_v_five():
    # return "5v5 not ready yet, hit the back button to get back to the home page"
    user = lc.User('na1', 'AMERICAS', '5pa6es')
    watcher = user.getWatcher()
    champNames = df.getChampNames(df.getChampList(watcher.data_dragon, "11.19.1"))
    redMessages = [ "Red 1", 
                    "Red 2", 
                    "Red 3",
                    "Red 4",
                    "Red 5"
                ]
    blueMessages = [ "Blue 1", 
                     "Blue 2", 
                     "Blue 3",
                     "Blue 4",
                     "Blue 5"
                ]
    noIcon = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/-1.png"
    redImages = [noIcon for x in range(0,5)]
    blueImages = [noIcon for x in range(0,5)]

    red_side_champs = []
    blue_side_champs = []

    for i in range(1,6):
        red_side_champs.append(flask.request.form.get(f'red_champion_{i}'))
        blue_side_champs.append(flask.request.form.get(f'blue_champion_{i}'))
    print(red_side_champs)
    print(blue_side_champs)
    display = False
    table_headers = ['Wins', 'Losses', 'Win Percentage', 'Wins Above Riot (W.A.R.)']
    rows = []
    matchupData = []
    blue_versus_data = []
    red_versus_data = []
    print(f'red champs: {red_side_champs}')
    result1 =  all(elem in champNames  for elem in red_side_champs)
    result2 =  all(elem in champNames  for elem in blue_side_champs)
    print(f'result1: {result1}, result2: {result2}')
    if (result1 == True) and (result2 == True):
        print('Enters into if')
        display = True
        table_headers[0] = 'Blue Side Wins'
        table_headers[1] = 'Red Side Wins'
        blueMessages = blue_side_champs
        redMessages = red_side_champs
        dbVersusFile = "data/champion_head_to_head.db"
        dbAllyFile = "data/champion_ally_stats.db"
        blue_versus_data = dbh.get_versus_data(dbVersusFile, blue_side_champs, red_side_champs)
        red_versus_data = dbh.get_versus_data(dbVersusFile, red_side_champs, blue_side_champs)
        pp(blue_versus_data, sort_dicts=False)
        pp(red_versus_data, sort_dicts=False)
        # Regenerate the champion image urls
        i = 0
        for champ in red_side_champs:
            imageUrl = 'https://ddragon.leagueoflegends.com/cdn/12.3.1/img/champion/'+champ+'.png'
            redImages[i] = imageUrl
            i = i + 1
        i = 0
        for champ in blue_side_champs:
            imageUrl = 'https://ddragon.leagueoflegends.com/cdn/12.3.1/img/champion/'+champ+'.png'
            blueImages[i] = imageUrl
            i = i + 1
    return flask.render_template("five_v_five.html", champions=champNames, blueMessages=blueMessages, redMessages=redMessages, display=display, table_headers=table_headers, red_versus=red_versus_data, blue_versus=blue_versus_data, redImages=redImages, blueImages=blueImages)

@app.route("/five_v_five_data", methods=['GET', 'POST'])
def five_v_five_data():
    # 'GET' request
    if flask.request.method == 'GET':
        message = {'greeting':'Hello from Flask!'}
        return flask.jsonify(message)  # serialize and use JSON headers
    # POST request
    if flask.request.method == 'POST':
        print(flask.request.get_json())  # parse as JSON
        data = flask.request.get_json()
        data = flask.jsonify(data)
        return data
        # return 'Sucesss', 200

@app.route("/draft_companion", methods=['GET', 'POST'])
def draft_companion():
    user = lc.User('na1', 'AMERICAS', '5pa6es')
    watcher = user.getWatcher()
    champNames = df.getChampNames(df.getChampList(watcher.data_dragon, "11.19.1"))
    redMessages = [ "Red 1", 
                    "Red 2", 
                    "Red 3",
                    "Red 4",
                    "Red 5"
                ]
    blueMessages = [ "Blue 1", 
                     "Blue 2", 
                     "Blue 3",
                     "Blue 4",
                     "Blue 5"
                ]
    noIcon = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/-1.png"
    redImages = [noIcon for x in range(0,5)]
    blueImages = [noIcon for x in range(0,5)]
    # return flask.render_template("draft_companion.html", champions=champNames, blueMessages=blueMessages, redMessages=redMessages, blueImages=blueImages, redImages=redImages)
    return "Currently under development, thank you for your patience"

@app.route("/table_test", methods=['GET', 'POST'])
def table_test():
    champion_data = []
    champion_dict = {}
    champName = 'Galio'
    headers = ['Versus', 'Wins', 'Losses', 'Win Percentage', 'Wins Above Riot (W.A.R.)']
    header_dict = {}
    for i in range(len(headers)):
        header_dict.update({i:headers[i]})
    print(header_dict)
    with sql.connect("data/champion_head_to_head.db") as db:
        c = db.cursor()
        execute_string = f"SELECT * FROM {champName};"
        rows = c.execute(execute_string).fetchall()
        # print(rows)
        for row in rows:
            versus, wins, losses, win_percentage, war_1, war_2 = row
            win_p = round(win_percentage*100.0, 2)
            war = round(war_2*100.0, 2)
            champion_data.append([versus, wins, losses, win_p, war])
    length = len(champion_data)
    for point in champion_data:
        champion_dict.update({point[0]:[point[0], point[1], point[2], point[3], point[4]]})
    return flask.render_template("table_test.html", name=champName, headers=header_dict, data=champion_dict, length=length)


if __name__ == '__main__':
	# Start the server
	app.run(port=8001, host='127.0.0.1', debug=True, use_evalex=False)


    # put a random button on the 1v1 and 5v5 matchup calcs
    # find statistical values for the data

    # <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>

# "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/-1.png"
# function communicateWithFlask(selectedColor){
#                 const champs = [];

#                 fetch('/five_v_five_data')
#                 .then(function (response) {
#                     return response.json();
#                 }).then(function (text) {
#                     console.log('GET response:');
#                     console.log(text.greeting); 
#                 });
#             }
