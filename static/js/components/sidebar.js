const toggleSidebar = document.querySelector("#toggle-sidebar");
const backBtn = document.querySelectorAll("#back");

const newProject = document.querySelectorAll("#new-project");
const newTeam = document.querySelectorAll("#new-team");

const popupContainer = document.querySelectorAll(".popup-container");
const projectPopup = document.querySelector("#project-popup");
const objectivePopup = document.querySelector("#objective-popup");
const teamPopup = document.querySelector("#team-popup");

// * function to slideout sidebar
function slideout_sidebar() {
    document.body.classList.remove('no-scroll');
    sidebar.style.transform = "translateX(-100%)"

    setTimeout(() => {
        sidebar.style.display = "none";
        openSidebar.style.display = "block";
    }, 300);
}

// & Event listener for sliding out sidebar
toggleSidebar.addEventListener('click', () => {
    slideout_sidebar();
})

// * function to open a popup container
function openPopup(popup) {
    popup.style.display = "flex";
    document.body.classList.add('no-scroll');

    setTimeout(() => {
        popup.style.opacity = "1"
    }, 100);
}

// * function to close a popup container
function closePopup() {
    document.body.classList.remove('no-scroll');
    popupContainer.forEach((elem) => {
        elem.style.opacity = "0";

        setTimeout(() => {
            elem.style.display = "none";
        }, 100);
    })
}

// & Event listener for add-project button
newProject.forEach((elem) => {
    elem.addEventListener('click', () => {
        openPopup(projectPopup);
    })
})

// & Event listener for add-team button
newTeam.forEach((elem) => {
    elem.addEventListener('click', () => {
        openPopup(teamPopup);
    })
})

// & Event listener to close popup
backBtn.forEach((btn) => {
    btn.addEventListener('click', closePopup);
})