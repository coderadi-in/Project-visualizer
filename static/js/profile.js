document.addEventListener('DOMContentLoaded', function () {
    const pic = document.querySelector("#pic");

    pic.addEventListener('change', () => {
        console.log("Image detected");
        const image = new Image();
        // Assuming you want to load the selected file into the image element
        const reader = new FileReader();
        reader.onload = (e) => {
            image.src = e.target.result;
            console.log(image.src);            
            const cropper = new Cropper(image); // Pass the image element to Cropper
        }
        // Read the selected file from the input element
        if (pic.files && pic.files[0]) {
            reader.readAsDataURL(pic.files[0]);
        }
    })
});