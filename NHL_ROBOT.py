import requests
import csv
from datetime import datetime, timedelta

#////////////////// FIRST PART

# From start, files have to be empty
open("FIN_player_stats.csv", "w").close()
open("finnish_players.csv", "w").close()
open("nhl_players_id.csv", "w").close()
open("player_stats.csv", "w").close()
open("standings.csv", "w").close()

team_codes = []

# Get all teams
res = requests.get('https://api-web.nhle.com/v1/standings/now')
for team in res.json()['standings']:
    team_codes.append(team['teamAbbrev']['default'])

print("Getting all players")
# CSV-file for all players
player_file = open('nhl_players_id.csv', "a", newline="", encoding="utf-8")
# CSV-file for finnish players
finnish_players_csv = 'finnish_players.csv'
finnish_players_file = open(finnish_players_csv, "a", newline="", encoding="utf-8")

# Write header to the finnish players file if it's empty
finnish_players_file.write("Team, Position, First Name, Last Name, Player ID\n")

# URL for player rosters
url = 'https://api-web.nhle.com/v1/roster/{}/current'
print("All players saved")
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
print("All FIN players saved")

# Close both files
player_file.close()
finnish_players_file.close()

print("Files are ready")

#////////////////// SECOND PART

# CSV-Files
FIN_player_csv = "finnish_players.csv"
FIN_stats_csv = "FIN_player_stats.csv"


# Search for the last game of player from last5Games-data
def get_latest_game_stats(player_id):
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Something went wrong searching {player_id} player stats . Status Code: {response.status_code}")
        return None
    
    data = response.json()

    # check last 5 games
    if 'last5Games' in data and data['last5Games']:
        # Sort games by dates
        latest_game = sorted(data['last5Games'], key=lambda x: x['gameDate'], reverse=True)[0]

        # Return different stats for goalie and field players
        if data.get('positionCode', '') == "G":  # Goalie
            return {
                "goals": latest_game.get("goals", None) or 0,
                "assists": latest_game.get("assists", None) or 0,
                "points": latest_game.get("points", None) or 0,
                "saves": latest_game.get("savePctg", None),
                "shotsAgainst": latest_game.get("shotsAgainst", None),
                "gameDate": latest_game.get("gameDate", "N/A"),
                "opponent": latest_game.get("opponentAbbrev", "N/A"),
                "team": latest_game.get("teamAbbrev", "N/A")
            }
        else:  # Defensemen and forwards
            return {
                "goals": latest_game.get("goals", None) or 0,
                "assists": latest_game.get("assists", None) or 0,
                "points": latest_game.get("points", None) or 0,
                "plusMinus": latest_game.get("plusMinus", None) or 0,
                "timeOnIce": latest_game.get("toi", None) or "00:00",
                "gameDate": latest_game.get("gameDate", "N/A"),
                "opponent": latest_game.get("opponentAbbrev", "N/A"),
                "team": latest_game.get("teamAbbrev", "N/A")
            }
    else:
        print(f"There wasn't games for this player {player_id} .")
        return None

# Load players from CSV
def load_players():
    players = {}
    try:
        with open(FIN_player_csv, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Jump over header
            for row in reader:
                if len(row) >= 5:  # Make sure there are enoungh rows
                    firstName, lastName, player_id = row[2], row[3], row[4]
                    name = f"{firstName} {lastName}"  # merge names
                    players[name] = int(player_id)
    except FileNotFoundError:
        print(f"This file {FIN_player_csv} wasn't anywhere to find.")
    return players

# Save player stats in CSV
def save_stats_to_csv(stats):
    with open(FIN_stats_csv, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["name", "goals", "assists", "points", "plusMinus", "time_on_ice", "game_date", "team", "opponent"])
        for stat in stats:
            writer.writerow(stat)
            

# Main
def main():
    players = load_players()
    player_stats = []
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    for name, player_id in players.items():
        print(f"Collect information of: {name} ({player_id})")
        stats = get_latest_game_stats(player_id)
        
        if stats and stats["gameDate"] == yesterday:
            if "saves" in stats:  # Goalie
                stat_row = (name, stats["goals"], stats["assists"], stats["points"], stats["saves"], stats["shotsAgainst"], stats["gameDate"], stats["team"], stats["opponent"])
            else:  # Field player
                stat_row = (name, stats["goals"], stats["assists"], stats["points"], stats["plusMinus"], stats["timeOnIce"], stats["gameDate"], stats["team"], stats["opponent"])
            player_stats.append(stat_row)
    

            
    # Save stats to csv
    save_stats_to_csv(player_stats)
    print(f"Stats saved in {FIN_stats_csv} file.")



if __name__ == "__main__":
    main()


#////////////////// THIRD PART

# CSV Files
GAME_SCORE_CSV = "game_scores.csv"

# NHL API URLs
SCORES_URL = "https://api-web.nhle.com/v1/score/now"


# Function to fetch and save game scores
def fetch_game_scores():
    response = requests.get(SCORES_URL)
    if response.status_code != 200:
        print(f"Error fetching game scores! Status code: {response.status_code}")
        return

    data = response.json()
    games = []

    for game in data.get("games", []):
        home_team = game["homeTeam"]["abbrev"]
        away_team = game["awayTeam"]["abbrev"]
        home_score = game["homeTeam"].get("score", 0)
        away_score = game["awayTeam"].get("score", 0)
        game_status = game.get("gameState", "N/A")  # LIVE, FINAL, PREVIEW

        games.append([away_team, away_score, home_team, home_score, game_status])

    with open(GAME_SCORE_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Away Team", "Away Score", "Home Team", "Home Score", "Status"])
        writer.writerows(games)

    print("✅ Game scores saved to CSV.")

fetch_game_scores()

# CSV File
# CSV File
STANDINGS_CSV = "standings.csv"



# NHL API URL
STANDINGS_URL = "https://api-web.nhle.com/v1/standings/now"

# Function to fetch and save standings, sorted by conference
def fetch_standings():
    response = requests.get(STANDINGS_URL)
    if response.status_code != 200:
        print(f"Error fetching standings! Status code: {response.status_code}")
        return

    data = response.json()

    eastern_standings = []
    western_standings = []

    for team in data['standings']:
        team_info = [
            team['teamName']['default'],
            team['goalFor'],
            team['goalAgainst'],
            team['wins'],
            team['losses'],
            team['ties'],
            team['points'],
            team['streakCode']
        ]

        # Sort teams into Eastern & Western Conference lists
        if team['conferenceName'] == "Eastern":
            eastern_standings.append(team_info)
        elif team['conferenceName'] == "Western":
            western_standings.append(team_info)

    # Write to CSV file
    with open(STANDINGS_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write Eastern Conference standings
        writer.writerow(["Eastern Conference"])
        writer.writerow(["Team", "Goals For", "Goals Against", "Wins", "Losses", "Ties", "Points", "Streak"])
        writer.writerows(eastern_standings)

        writer.writerow([])  # Empty row for spacing

        # Write Western Conference standings
        writer.writerow(["Western Conference"])
        writer.writerow(["Team", "Goals For", "Goals Against", "Wins", "Losses", "Ties", "Points", "Streak"])
        writer.writerows(western_standings)

    print("✅ Standings sorted by conference and saved to CSV.")

# Run the function
fetch_standings()
