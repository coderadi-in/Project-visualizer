const notificationSection = document.querySelector(".notifications-section");
const notificationBody = document.querySelector(".notifications-section .body");
const socket = io();

// * Creating IntersectionObserver to check if notification is seen.
const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            socket.emit('notification-seen', parseInt(entry.target.id));
        }
    });
}, {
    threshold: 0.6, 
    rootMargin: '0px'
});

// & Observe notifications.
const Notifications = document.querySelectorAll('.notifications-section .notification');
Notifications.forEach((element) => {
    observer.observe(element);
});

// * Function to toggle notifications section
function toggleNotificationsSection() {
    notificationSection.classList.toggle('active');
    if (notificationSection.classList.contains("active")) {
        notificationBody.style.opacity = "0";
        notificationBody.style.height = "0px";

        setTimeout(() => {
            notificationBody.style.display = "none";
        }, 100);
    }
    else {
        notificationBody.style.display = "flex";

        setTimeout(() => {
            notificationBody.style.opacity = "1";
            notificationBody.style.height = "auto";
        }, 100);
    }
}

// & Event listener for opening & closing notifications section.
notificationSection.addEventListener('click', toggleNotificationsSection);