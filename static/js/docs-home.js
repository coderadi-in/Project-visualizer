const themeBtn = document.querySelector("#theme-btn");
const themeIcon = document.querySelector("#theme-btn .icon");
const defaultTheme = 'light';

// * Function to get saved theme
function getSavedTheme() {
    let theme = localStorage.getItem('theme');
    if (!theme) {return defaultTheme;}
    else {return theme;}
}

// * Function to save theme
function saveTheme(theme) {localStorage.setItem('theme', theme);}

// * Function to set saved theme on page
function setTheme() {
    let savedTheme = getSavedTheme();
    let rotateAngle = (savedTheme == 'light') ? 0 : 180;
    let themeIconSrc = `/static/assets/icons/theme-${savedTheme}.png`;
    themeIcon.src = themeIconSrc;
    themeIcon.style.transform = `rotate(${rotateAngle}deg)`;
    document.body.classList.add(savedTheme);
}

// * Function to update theme on page
function updateTheme() {
    let savedTheme = getSavedTheme();
    document.body.classList.remove(savedTheme);
    let newTheme = (savedTheme == 'light') ? 'dark' : 'light';
    saveTheme(newTheme);
    setTheme();
}

// & Event listener for themeBtn click
themeBtn.addEventListener('click', () => {updateTheme();});
setTheme();