const newObjective = document.querySelector("#add-objective");
const checkboxes = document.querySelectorAll(".checkbox");
const deletebtns = document.querySelectorAll(".delete-objective");
const deleteBtn = document.querySelector("#delete-project");;

const projectId = document.querySelector("#project-id").innerHTML;
const userId = document.querySelector("#userid").innerHTML;
const viewerId = document.querySelector("#viewer-id").innerHTML;
const teamId = document.querySelector("#team-id") ? document.querySelector("#team-id").innerHTML : '0';

const chartElem = document.querySelector("#contribution-chart")
const chartArea = chartElem ? chartElem.getContext('2d') : null;
const chartColor = document.body.dataset.chartColor;
const chartType = document.body.dataset.chartType;

const colorScheme = {
    timelineBg: ["#4C8EFF", "#FFFFFF00"],
    timelineHover: ["#C0D8FF", "#808080"],
    taskBg: ["#93FF93", "#FF9393"],
    taskHover: ["#CCFFCC", "#FFCCCC"],
    contributionBg: "#CCFFCC",
    contributionBorder: "#93FF93"
};

const classic = {
    blue: { ...colorScheme },
    green: { ...colorScheme },
    red: { ...colorScheme },
    yellow: { ...colorScheme }
};

const modern = {
    blue: {
        timelineBg: ["#7CACFF", "#FFFFFF00"],
        timelineHover: ["#C0D8FF", "#808080"],
        taskBg: ["#4C8EFF", "#7CACFF"],
        taskHover: ["#89B4FF", "#9BC0FF"],
        contributionBg: "#9BC0FF",
        contributionBorder: "#89B4FF",
    },
    green: {
        timelineBg: ["#7CFFAC", "#FFFFFF00"],
        timelineHover: ["#C0FFD8", "#808080"],
        taskBg: ["#36C76B", "#7CFFAC"],
        taskHover: ["#89FFC4", "#9BFFD5"],
        contributionBg: "#9BFFD5",
        contributionBorder: "#89FFC4",
    },
    red: {
        timelineBg: ["#FF7CAC", "#FFFFFF00"],
        timelineHover: ["#FFC0D8", "#808080"],
        taskBg: ["#FF4C8E", "#FF7CAC"],
        taskHover: ["#FF8989", "#FF9B9B"],
        contributionBg: "#FF9B9B",
        contributionBorder: "#FF8989",
    },
    yellow: {
        timelineBg: ["#F0F084", "#FFFFFF00"],
        timelineHover: ["#FFFFD0", "#808080"],
        taskBg: ["#DBDB53", "#F0F084"],
        taskHover: ["#FDFF89", "#FFF09B"],
        contributionBg: "#FFF09B",
        contributionBorder: "#FDFF89",
    },
};

const currentScheme = (chartColor == 'classic') ? classic : modern;
const currentAccent = document.body.dataset.accent;

// * function to send socket msg to server
function transmit(namespace, data) {
    socket.emit(namespace, {
        'obj_id': data,
        'team_id': parseInt(teamId),
        'user_id': parseInt(userId),
        'viewer_id': parseInt(viewerId),
        'route': parseInt(projectId),
    })
}

async function rednerContributionChart() {
    if (teamId !== '0') {
        const response = await fetch(`/api/team/members/contribution?team_id=${teamId}`);
        const data = await response.json();

        const contributionChart = new Chart(chartArea, {
            type: 'bar',
            data: {
                labels: data.members,
                datasets: [{
                    label: "Contribution",
                    data: data.contribution,
                    backgroundColor: currentScheme[currentAccent].contributionBg,
                    borderColor: currentScheme[currentAccent].contributionChart,
                    borderWidth: 1,
                    hoverBackgroundColor: currentScheme[currentAccent].contributionBg,
                    hoverBorderColor: currentScheme[currentAccent].contributionChart,
                    indexAxis: 'y',
                }]
            }
        });
    } else {
        chartElem.style.display = 'none';
    }
}

async function renderTimelineChart() {
    const response = await fetch(`/api/project/${projectId}/time-data?userid=${viewerId}&teamid=${teamId}`);
    const data = await response.json();

    if (data.left_time !== undefined && data.spent_time !== undefined) {
        const timeline_chart = new Chart(
            document.querySelector("#timeline-chart").getContext('2d'), {
            type: chartType,
            data: {
                labels: ["Left time", "Spent time"],
                datasets: [{
                    label: "Timeline",
                    data: [data.left_time, data.spent_time],
                    backgroundColor: currentScheme[currentAccent].timelineBg,
                    hoverBackgroundColor: currentScheme[currentAccent].timelineHover,
                    hoverOffset: 5,
                    borderColor: "#00000000",
                }]
            }
        });
    }
}

async function renderTaskChart() {
    const response = await fetch(`/api/project/${projectId}/task-data?userid=${viewerId}&teamid=${teamId}`)
    const data = await response.json();

    if (data.completed !== undefined && data.incomplete !== undefined) {
        const task_chart = new Chart(
            document.querySelector("#task-chart").getContext('2d'), {
            type: chartType,
            data: {
                labels: ["Completed", "Incomplete"],
                datasets: [{
                    label: "Tasks",
                    data: [data.completed, data.incomplete],
                    backgroundColor: currentScheme[currentAccent].taskBg,
                    hoverBackgroundColor: currentScheme[currentAccent].taskHover,
                    hoverOffset: 5,
                    borderColor: "#00000000",
                }]
            }
        });
    }
}

// | socket listener for marking objectives
socket.on('mark-obj-callback', (data) => {
    if (data.status == 200) {
        window.location.reload();
    } else {
        alert("Something went wrong.")
    }
})

// | socket listener for delete objectives
socket.on('del-obj-callback', (data) => {
    if (data.status == 200) {
        window.location.reload();
    } else {
        alert("Something went wrong.")
    }
})

// & Event listerner for add-objective button
if (newObjective) {
    newObjective.addEventListener('click', () => {
        openPopup(objectivePopup);
    })
}

// & Event listener to close popup
if (backBtn) {
    backBtn[1].addEventListener('click', () => {
        closePopup();
    })
}

// & Event listener for checkbox markings
if (checkboxes) {
    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener('click', (event) => {
            transmit('mark-obj', event.currentTarget.dataset.objId);
        });
    });
}

// & Event listener for delete button clicks
if (deletebtns) {
    deletebtns.forEach((btn) => {
        btn.addEventListener('click', (event) => {
            transmit('delete-obj', event.currentTarget.dataset.objId);
        })
    })
}

// & Event listener for delete-project
if (deleteBtn) {
    deleteBtn.addEventListener('click', () => {
        confirmation = confirm("Are you sure to delete this project?");

        if (confirmation) {
            window.open(`/projects/delete?project-id=${projectId}`)
        }
    })
}

renderTimelineChart();
renderTaskChart();
rednerContributionChart();