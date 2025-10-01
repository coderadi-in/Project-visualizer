const renewBtn = document.querySelector("#renew-hosting");

renewBtn.addEventListener('click', () => {
    confirmation = confirm("Renew hosting?")

    if (confirmation) {window.open('/admin/renew');}
})