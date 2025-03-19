document.addEventListener("DOMContentLoaded", function() {
    console.log("Script is running!"); // Debugging

    const gameResults = document.getElementById('game-results');
    const playerStats = document.getElementById('player-stats');
    const easternStandings = document.getElementById('eastern-standings');
    const westernStandings = document.getElementById('western-standings');

    if (!gameResults || !playerStats || !easternStandings || !westernStandings) {
        console.error("One or more elements are missing from the HTML.");
        return;
    }

    loadData(gameResults, playerStats, easternStandings, westernStandings);

    // MutationObserver to replace DOMSubtreeModified
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            console.log(mutation);
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });
});

async function loadData(gameResults, playerStats, easternStandings, westernStandings) {
    try {
        const response = await fetch('nhl_data.json'); // Ensure this file exists in GitHub
        if (!response.ok) throw new Error('Failed to load JSON');

        const data = await response.json();
        console.log("Data loaded:", data); // Debugging

        gameResults.innerHTML = data.games.map(game => 
            `<p>${game.matchup} (${game.status})</p>`
        ).join('');

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

        easternStandings.innerHTML = data.standings.filter(team => team.conference === 'Eastern')
            .map(team => `<p>${team.team}: ${team.wins}W - ${team.losses}L, ${team.points}PTS</p>`).join('');

        westernStandings.innerHTML = data.standings.filter(team => team.conference === 'Western')
            .map(team => `<p>${team.team}: ${team.wins}W - ${team.losses}L, ${team.points}PTS</p>`).join('');

    } catch (error) {
        console.error("Error loading data:", error);
    }
}