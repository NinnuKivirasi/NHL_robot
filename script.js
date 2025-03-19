async function loadData() {
    try {
        const response = await fetch('nhl_data.json');  // Make sure this JSON file exists in your GitHub repo
        if (!response.ok) {
            throw new Error('Failed to load JSON');
        }
        const data = await response.json();
        console.log(data); // Debugging: check if data is loaded

        // Display game results
        const gameResults = document.getElementById('game-results');
        gameResults.innerHTML = data.games.map(game => 
            `<p>${game.matchup} (${game.status})</p>`).join('');

        // Display Finnish player stats (only relevant ones)
        const playerStats = document.getElementById('player-stats');
        playerStats.innerHTML = data.players
            .filter(player => 
                (player.position !== 'G' && (player.goals > 0 || player.assists > 0 || player.points > 0)) || 
                (player.position === 'G' && player.saves !== null && player.shotsAgainst !== null)
            )
            .map(player => 
                player.position === 'G' 
                    ? `<p>${player.name} (G): ${player.saves} SV, ${player.shotsAgainst} SA vs ${player.opponent}</p>` 
                    : `<p>${player.name}: ${player.goals}G, ${player.assists}A, ${player.points}P vs ${player.opponent}</p>`
            )
            .join('');

        // Display standings (grouped by conferences)
        const easternStandings = document.getElementById('eastern-standings');
        const westernStandings = document.getElementById('western-standings');

        const easternTeams = data.standings.filter(team => team.conference === 'Eastern');
        const westernTeams = data.standings.filter(team => team.conference === 'Western');

        easternStandings.innerHTML = easternTeams.map(team =>
            `<p>${team.team}: ${team.wins}W - ${team.losses}L, ${team.points}PTS</p>`).join('');

        westernStandings.innerHTML = westernTeams.map(team =>
            `<p>${team.team}: ${team.wins}W - ${team.losses}L, ${team.points}PTS</p>`).join('');

    } catch (error) {
        console.error("Error loading data:", error);
    }
}

// Load data when the page is loaded
document.addEventListener("DOMContentLoaded", loadData);
