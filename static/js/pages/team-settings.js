const visibilitySwitch = document.querySelector("#switch-body");
const visibilityIndicator = document.querySelector("#switch-ball");
const deleteBtn = document.querySelector("#delete-team");
const addModerators = document.querySelectorAll(".add-moderator");
const removeModerators = document.querySelectorAll(".remove-moderator");
const teamId = document.querySelector("#team-id").innerHTML;

// * Socket route to check if team settings is updated
socket.on('team-settings-callback', (data) => {
    if (data.status == 200) { window.location.reload(); }
})

// * socket route to check if member is promoted
socket.on('add-moderator-callback', (data) => {
    if (data.status == 200) { window.location.reload(); }
})

// * socket route to check if member is demoted
socket.on('remove-moderator-callback', (data) => {
    if (data.status == 200) { window.location.reload(); }
})

// * socket route to check if member is removed
socket.on('remove-member-callback', (data) => {
    if (data.status == 200) { window.location.reload(); }
})

// & Event listener to trigger visibility btn
visibilitySwitch.addEventListener('click', () => {
    visibilityIndicator.classList.toggle('private');

    if (visibilityIndicator.classList.contains('private')) {
        socket.emit('team-settings', {
            teamId: teamId,
            private: true,
        })
    } else {
        socket.emit('team-settings', {
            teamId: teamId,
            private: false,
        })
    }
})

// & Event listener to trigger delete-team btn
deleteBtn.addEventListener('click', () => {
    confirmation = confirm("Are you sure to delete this team?")

    if (confirmation) {
        window.open(`/teams/${teamId}/delete`, "_self");
    }
})

// & Event listeners for members section
document.addEventListener('click', (event) => {
    element = event.target.parentElement
    if (element.classList.contains('add-moderator')) {
        socket.emit('add-moderator', {
            memId: element.dataset.memId,
            teamId: teamId
        })

    } else if (element.classList.contains('remove-moderator')) {
        socket.emit('remove-moderator', {
            memId: element.dataset.memId,
            teamId: teamId
        })

    } else if (element.classList.contains('remove-member')) {
        confirmation = confirm("Are you sure to delete this member?")

        if (confirmation) {
            socket.emit('remove-member', {
                memId: element.dataset.memId,
                teamId: teamId
            })
        }

    }
})