const visibilitySwitch = document.querySelector("#switch-body");
const visibilityIndicator = document.querySelector("#switch-ball");
const deleteBtn = document.querySelector("#delete-project");
const projectId = document.querySelector("#project-id").innerHTML;

// & Socket listener for update visibility callback
socket.on('project-settings-callback', (data) => {
    if (data.status == 200) {window.location.reload();}
    else if (data.status == 500) {alert('Something went wrong.')}
    else {alert("Project not found."); window.location.reload();}
})

// & Event listener for update visibility button
visibilitySwitch.addEventListener('click', () => {
    visibilityIndicator.classList.toggle('private');

    if (visibilityIndicator.classList.contains('private')) {
        socket.emit('project-settings', {
            projectId: projectId,
            private: true,
        })
    } else {
        socket.emit('project-settings', {
            projectId: projectId,
            private: false,
        })
    }
})

// & Event listener for delete button
deleteBtn.addEventListener('click', () => {
    confirmation = confirm("Are your sure to delete this project?")

    if (confirmation) {
        window.open(`/projects/delete?project-id=${projectId}`, "_self");
    }
})