const downloadDB = document.querySelector("#download-db");
const uploadDB = document.querySelector("#upload-db")
const downloadDBPopup = document.querySelector("#download-db-popup");
const uplaodDBPopup = document.querySelector("#upload-db-popup");

// & Event listener for downloadDB click
downloadDB.addEventListener('click', () => {
    openPopup(downloadDBPopup);
})

// & Event listener for uploadDB click
uploadDB.addEventListener('click', () => {
    openPopup(uplaodDBPopup);
})