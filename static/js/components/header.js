const openSidebar = document.querySelector("#open-sidebar");
const sidebar = document.querySelector('.sidebar');
const notificationBtn = document.querySelector("#notifications");

// * function to slideout sidebar
function slidein_sidebar() {
    sidebar.style.display = "flex";
    openSidebar.style.display = "none";
    document.body.classList.add('no-scroll');
    
    setTimeout(() => {
        sidebar.style.transform = "translateX(0)";
    }, 100);
}

// * function to toggle notifications section visibility by default
function NotificationsVisibility() {
    if (localStorage.getItem('notifications-section') == 'open') {
        notificationSection.style.display = "flex";
        notificationSection.style.opacity = "1";

    } else {
        notificationSection.style.display = "none";
        notificationSection.style.opacity = "0";
    }
}

// * function to toggle notifications section visibility.
function toggleNotificationsVisibility() {
    notificationSection.classList.toggle('active')
    if (notificationSection.classList.contains('active')) {
        notificationSection.style.opacity = "0";
        localStorage.setItem('notifications-section', 'close');

        setTimeout(() => {
            notificationSection.style.display = "none";
        }, 100);

    } else {
        notificationSection.style.display = "flex";
        localStorage.setItem('notifications-section', 'open');

        setTimeout(() => {
            notificationSection.style.opacity = "1";
        }, 100);
    }
}

// & Event listener for slideing in sidebar
openSidebar.addEventListener('click', () => {
    slidein_sidebar();
})

// & Event listener for prevent default browser actions
document.addEventListener('keydown', (e) => {
    const isCtrlSlash = e.ctrlKey && e.key === '/';
    if (isCtrlSlash) e.preventDefault();
});

// & Event listener for focusing the search input
document.addEventListener('keyup', (e) => {
    if (e.ctrlKey && e.key == '/') {e.preventDefault(); document.querySelector("#search").focus()}
    if (e.key == 'Escape') {e.preventDefault(); closePopup()};
})

// & Event listener for notifications section visibility
notificationBtn.addEventListener('click', toggleNotificationsVisibility);
NotificationsVisibility();