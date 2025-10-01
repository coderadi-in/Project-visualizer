const notifyBtn = document.querySelector("#notify");
const newsletterBtn = document.querySelector("#newsletter");
const newTableBtn = document.querySelector("#new-table");
const newRowBtn = document.querySelector("#new-row");

const notifyPopup = document.querySelector("#notify-popup");
const newsletterPopup = document.querySelector("#newsletter-popup");
const newTablePopup = document.querySelector("#new-table-popup");
const newRowPopup = document.querySelector("#new-row-popup");

// * function to open a popup container
function openPopup(popup) {
    popup.style.display = "flex";
    document.body.classList.add('no-scroll');

    setTimeout(() => {
        popup.style.opacity = "1"
    }, 100);
}

// & Event listener for notifyBtn click
notifyBtn.addEventListener('click', () => {
    openPopup(notifyPopup);
})

// & Event listener for newsletterBtn click
newsletterBtn.addEventListener('click', () => {
    openPopup(newsletterPopup);
})