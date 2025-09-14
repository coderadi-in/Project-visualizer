const notifications = document.querySelectorAll(".flash");

// * function to create notification slidein animation
function applyNotificationSlideIn(array, index=0) {
    if (index >= array.length) {return;}

    array[index].style.transform = "translateX(0)"
    array[index].style.opacity = 1;

    applyNotificationSlideIn(array, index+1);
}

// * function to remove notification slidein animation
function removeNotificationSlideIn(array, index=0) {
    if (index >= array.length) {return;}

    setTimeout(() => {
        array[index].style.transform = "translateX(-100%)";
        array[index].style.opacity = 0;
        setTimeout(() => {
            array[index].style.display = "none";
        }, 100);
    }, 3000);

    removeNotificationSlideIn(array, index+1);
}

if (notifications) {
    applyNotificationSlideIn(notifications);
    removeNotificationSlideIn(notifications);
}