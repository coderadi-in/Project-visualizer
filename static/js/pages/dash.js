// & Event listener for add-project button
document.querySelectorAll("#new-project").forEach((elem) => {
    elem.addEventListener('click', () => {
        openPopup(projectPopup);
    })
})