document.querySelectorAll("#new-team").forEach((elem) => {
    elem.addEventListener('click', () => {
        openPopup(teamPopup);
    })
})