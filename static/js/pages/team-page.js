const newMem = document.querySelector("#new-member");
const memPopup = document.querySelector("#mem-popup");
const chartArea = document.querySelector("#contribution-chart").getContext('2d');
const teamId = document.querySelector("#team-id").innerHTML;

// * function to render contribution chart
async function rednerContributionChart() {
    const response = await fetch(`/api/team/members/contribution?team_id=${teamId}`)
    const data = await response.json()

    const contributionChart = new Chart(chartArea, {
        type: 'bar',
        data: {
            labels: data.members,
            datasets: [{
                label: "Contribution",
                data: data.contribution,
                backgroundColor: "#CCFFCC",
                borderColor: "#93FF93",
                borderWidth: 1,
                hoverBackgroundColor: "#CCFFCC",
                hoverBorderColor: "#93FF93",
                indexAxis: 'y'
            }]
        }
    })
}

// & Event listener for opening new-member popup
if (newMem) {
    newMem.addEventListener('click', () => {
        openPopup(memPopup)
    })
}

rednerContributionChart();