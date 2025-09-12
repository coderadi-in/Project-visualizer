const users = document.querySelectorAll(".user");

function addAnim(array, index=0) {
    if (index >= array.length) {return;}
    
    setTimeout(() => {
        array[index].style.transform = "translateY(0)";
        array[index].style.opacity = "1";
        addAnim(array, index+1);
    }, 100);
}

addAnim(users);