# DraftCompanion
DraftCompanion is a reference website for competitve esports (League of Legends), where players of all levels can use the tools provided to gain strategic advantages.
## Important Knowledge
### Vocabulary
### What is League of Legends?

## Project Description
### What DraftCompanion Does
### Technologies Used
- Python 3.9.6
- Bootstrap 5.1.3
- Flask 2.0.2
- RiotWatcher 3.2
- Jinja2 3.0.3
- Pandas 1.3.3
- Numpy 1.23.3
- jQuery 1.7.1
- Google Cloud
### Moving Forward
- (As of 10/12) Some of the more recent updates I have done on the backend have not made their way to the live site yet, but I plan on pushing those changes soon
- The namesake for this website, the DraftCompanion, is currently the only tool I had planned that has not shipped. The DraftCompanion tool will give users the ability to analyze their draft while it is happening and will give them suggestions on who they should pick or ban next to maximize their advantage over their opponent.

## How to use the DraftCompanion Web App
### Home Page
![](Images/demo/homepage.png)
### Champion Data Tables
The first two tools the DraftCompanion offers to its users are the ally and versus data tables. These tables represent the data that has been collected for each champion. The versus tables show the performance of a given champion when another champion is on the enemy team. The ally tables show the performance of a given champion when they have any other champion on their team. These tables give users the ability to see what pairings or matchups their champion excels at and where they might run into problems.

![](Images/demo/champion_data_versus.png)
![](Images/demo/champion_data_ally.png)


### One v One Calculator
The third tool offered by the DraftCompanion is the one v one calculator. This gives users a quick and easy way to see how one champion does when playing against another. Users will most likely use this tool when they want to see how the champion they chose matches up against their lane opponent.


![](Images/demo/one_v_one_calculator.png)


### Five v Five Team Composition Analyzer
The fourth tool offered by the DraftCompanion is the five v five team composition analyzer. This gives users the ability to see how their team composition matches up against their opponents. The percentage shown next to the champion is their collective winrate against each of the champions on the enemy team. At the bottom of the page, the ‘Team Win Rate’ section shows which team has the edge over the other and currently serves as a loose indicator of who should win the game.


![](Images/demo/five_v_five_calculator.png)


If the user wants to see more information about each champions individual matchups, they can change over to the detailed view using the button at the top of the page, which provides a more in-depth look at how each champion has performed against the enemy team.


![](Images/demo/five_v_five_calculator_detailed.png)
