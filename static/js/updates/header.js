const nav = document.querySelector('.nav');

// * Function to open sidebar
function openSidebar() {
    console.log("opening");
    nav.classList.add("open");
    nav.style.display = 'flex';

    setTimeout(() => {
        nav.style.opacity = "1";
        nav.style.transform = "translateX(0)";
    }, 100);
}

// * Function to close sidebar
function closeSidebar() {
    console.log("closing");
    nav.classList.remove("open");
    nav.style.opacity = "0";
    nav.style.transform = "translateX(-100%)";

    setTimeout(() => {
        nav.style.display = 'none';
    }, 300); // give enough time for transition
}

document.addEventListener('click', (e) => {
    const clickedMenuBar = e.target.closest('.menu-bar');
    if (clickedMenuBar) {
        // check sidebar state instead of button state
        if (nav.classList.contains('open')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }
});
