import requests
import csv

# From start, files have to be empty
open("FIN_player_stats.csv", "w").close()
open("finnish_players.csv", "w").close()
open("nhl_players_id.csv", "w").close()
open("player_stats.csv", "w").close()

team_codes = []

# Get all teams
res = requests.get('https://api-web.nhle.com/v1/standings/now')
for team in res.json()['standings']:
    team_codes.append(team['teamAbbrev']['default'])

# CSV-file for all players
player_file = open('nhl_players_id.csv', "a", newline="", encoding="utf-8")
# CSV-file for finnish players
finnish_players_csv = 'finnish_players.csv'
finnish_players_file = open(finnish_players_csv, "a", newline="", encoding="utf-8")

# Write header to the finnish players file if it's empty
finnish_players_file.write("Team, Position, First Name, Last Name, Player ID\n")

# URL for player rosters
url = 'https://api-web.nhle.com/v1/roster/{}/current'

# Go through all teams
for team in team_codes:
    res = requests.get(url.format(team))
    players = [player for position in ['forwards', 'defensemen', 'goalies'] for player in res.json()[position]]
    
    for player in players:
        player_info = f'{team}, {player["positionCode"]}, {player["firstName"]["default"]}, {player["lastName"]["default"]}, {player["id"]}, {player["birthCountry"]}\n'
        
        # Write all players to the nhl_players_id.csv
        player_file.write(player_info)
        
        # Write only finnish players to finnish_players.csv
        if player["birthCountry"] == "FIN":
            finnish_players_file.write(f'{team}, {player["positionCode"]}, {player["firstName"]["default"]}, {player["lastName"]["default"]}, {player["id"]}\n')

# Close both files
player_file.close()
finnish_players_file.close()

print("Files are ready")

#_____________________________________________________________________________________________________________________



