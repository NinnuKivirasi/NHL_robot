import requests
import pandas as pd

# Hae sarjataulukon data API:sta
response = requests.get("https://api-web.nhle.com/v1/standings/now")
data = response.json()

# Muodosta DataFrame
eastern_standings = []
western_standings = []

for team_record in data['standings']:
    team_info = {
        "Conference": team_record['conferenceName'],
        "Date": team_record['date'],
        "Rank": team_record['conferenceSequence'],
        'Team': team_record['teamName']['default'],
        'Goals made/against': team_record['goalFor'] - team_record['goalAgainst'],
        'Wins': team_record['wins'],
        'Losses': team_record['losses'],
        'Ties': team_record['ties'],
        'Points': team_record['points'],
        'Streak': team_record['streakCode']
    }
    if team_record['conferenceName'] == 'Eastern':
        eastern_standings.append(team_info)
    elif team_record['conferenceName'] == 'Western':
        western_standings.append(team_info)

# Luo DataFrame
df_eastern = pd.DataFrame(eastern_standings)
df_western = pd.DataFrame(western_standings)

# Näytä sarjataulukot
print("Eastern Conference Standings:")
print(df_eastern)
print("\nWestern Conference Standings:")
print(df_western)