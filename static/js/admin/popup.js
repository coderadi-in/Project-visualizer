// * function to close a popup container
function closePopup() {
    console.log("closing");    
    document.body.classList.remove('no-scroll');
    const popupContainer = document.querySelectorAll('.popup-container');
    popupContainer.forEach((elem) => {
        elem.style.opacity = "0";

        setTimeout(() => {
            elem.style.display = "none";
        }, 100);
    })
}

// & DOM Event listener for back-btn click
document.addEventListener('click', (e) => {
    const backBtn = e.target.closest('.back-btn');
    if (backBtn) {closePopup();}
})