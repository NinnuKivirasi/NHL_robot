import requests
import csv
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Ensimmäinen osa: Hae pelaajatiedot ja tallenna CSV-tiedostoihin
def fetch_and_save_players():
    # Tyhjennä tiedostot alussa
    open("FIN_player_stats.csv", "w").close()
    open("finnish_players.csv", "w").close()
    open("nhl_players_id.csv", "w").close()
    open("player_stats.csv", "w").close()

    team_codes = []

    # Hae kaikki joukkueet
    res = requests.get('https://api-web.nhle.com/v1/standings/now')
    for team in res.json()['standings']:
        team_codes.append(team['teamAbbrev']['default'])

    print("Getting all players")
    # CSV-tiedosto kaikille pelaajille
    player_file = open('nhl_players_id.csv', "a", newline="", encoding="utf-8")
    # CSV-tiedosto suomalaisille pelaajille
    finnish_players_csv = 'finnish_players.csv'
    finnish_players_file = open(finnish_players_csv, "a", newline="", encoding="utf-8")

    # Kirjoita otsikko suomalaisille pelaajille, jos tiedosto on tyhjä
    finnish_players_file.write("Team, Position, First Name, Last Name, Player ID\n")

    # URL pelaajalistoille
    url = 'https://api-web.nhle.com/v1/roster/{}/current'
    print("All players saved")
    # Käy läpi kaikki joukkueet
    for team in team_codes:
        res = requests.get(url.format(team))
        players = [player for position in ['forwards', 'defensemen', 'goalies'] for player in res.json()[position]]
        
        for player in players:
            player_info = f'{team}, {player["positionCode"]}, {player["firstName"]["default"]}, {player["lastName"]["default"]}, {player["id"]}, {player["birthCountry"]}\n'
            
            # Kirjoita kaikki pelaajat nhl_players_id.csv-tiedostoon
            player_file.write(player_info)

            # Kirjoita vain suomalaiset pelaajat finnish_players.csv-tiedostoon
            if player["birthCountry"] == "FIN":
                finnish_players_file.write(f'{team}, {player["positionCode"]}, {player["firstName"]["default"]}, {player["lastName"]["default"]}, {player["id"]}\n')
    print("All FIN players saved")

    # Sulje molemmat tiedostot
    player_file.close()
    finnish_players_file.close()

    print("Files are ready")

# Toinen osa: Hae pelaajien viimeisimmät pelitilastot ja tallenna CSV-tiedostoon
def fetch_and_save_player_stats():
    FIN_player_csv = "finnish_players.csv"
    FIN_stats_csv = "FIN_player_stats.csv"

    def get_latest_game_stats(player_id):
        url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Something went wrong searching {player_id} player stats . Status Code: {response.status_code}")
            return None
        
        data = response.json()

        # Tarkista viimeiset 5 peliä
        if 'last5Games' in data and data['last5Games']:
            # Järjestä pelit päivämäärän mukaan
            latest_game = sorted(data['last5Games'], key=lambda x: x['gameDate'], reverse=True)[0]

            # Palauta eri tilastot maalivahdeille ja kenttäpelaajille
            if data.get('positionCode', '') == "G":  # Maalivahti
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
            else:  # Puolustajat ja hyökkääjät
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

    def load_players():
        players = {}
        try:
            with open(FIN_player_csv, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)  # Hyppää otsikon yli
                for row in reader:
                    if len(row) >= 5:  # Varmista, että rivejä on tarpeeksi
                        firstName, lastName, player_id = row[2], row[3], row[4]
                        name = f"{firstName} {lastName}"  # Yhdistä nimet
                        players[name] = int(player_id)
        except FileNotFoundError:
            print(f"This file {FIN_player_csv} wasn't anywhere to find.")
        return players

    def save_stats_to_csv(stats):
        with open(FIN_stats_csv, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["name", "goals", "assists", "points", "saves", "shotsAgainst", "plusMinus", "time_on_ice", "game_date", "team", "opponent"])
            for stat in stats:
                writer.writerow(stat)

    players = load_players()
    player_stats = []
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    for name, player_id in players.items():
        print(f"Collect information of: {name} ({player_id})")
        stats = get_latest_game_stats(player_id)
        
        if stats and stats["gameDate"] == yesterday:
            if "saves" in stats:  # Maalivahti
                stat_row = (name, stats["goals"], stats["assists"], stats["points"], stats["saves"], stats["shotsAgainst"], stats["gameDate"], stats["team"], stats["opponent"])
            else:  # Kenttäpelaaja
                stat_row = (name, stats["goals"], stats["assists"], stats["points"], stats["plusMinus"], stats["timeOnIce"], stats["gameDate"], stats["team"], stats["opponent"])
            player_stats.append(stat_row)

    save_stats_to_csv(player_stats)
    print(f"Stats saved in {FIN_stats_csv} file.")

# Päivitä HTML-sivu
def update_html():
    with open("index.html", "r") as file:
        soup = BeautifulSoup(file, "html.parser")

    standings_div = soup.find(id="standings")
    if standings_div is None:
        print("Virhe: Elementtiä, jonka id on 'standings', ei löytynyt.")
        return

    standings_div.clear()  # Poista vanha sisältö

    with open("FIN_player_stats.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Hyppää otsikon yli
        for row in reader:
            print(row)  # Tulosta rivi nähdäksesi sen sisällön
            if len(row) < 11:
                continue  # Hyppää tämän rivin yli, jos elementtejä ei ole tarpeeksi

            player_info = f"""
            <div class="player">
                <h2>{row[0]}</h2>
                <p>Goals: {row[1]}</p>
                <p>Assists: {row[2]}</p>
                <p>Points: {row[3]}</p>
                <p>Saves: {row[4]}</p>
                <p>Shots Against: {row[5]}</p>
                <p>Plus/Minus: {row[6]}</p>
                <p>Time on Ice: {row[7]}</p>
                <p>Game Date: {row[8]}</p>
                <p>Team: {row[9]}</p>
                <p>Opponent: {row[10]}</p>
            </div>
            """
            standings_div.append(BeautifulSoup(player_info, "html.parser"))

    with open("index.html", "w") as file:
        file.write(str(soup))

    print("HTML page updated")

# Suorita tehtävät
fetch_and_save_players()
fetch_and_save_player_stats()
update_html()