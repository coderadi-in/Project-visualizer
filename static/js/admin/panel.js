const socket = io();
let isProcessing = false;

// & Event listener for seenBtn click
document.addEventListener('click', (event) => {
    const seenBtn = event.target.closest('.seen-btn');

    if (seenBtn && !isProcessing) {
        isProcessing = true;
        socket.emit('mark-feed', {feedId: seenBtn.dataset.feedId})
    }
})

// * Socket listener for seenBtn click callback
socket.on('mark-feed-callback', (data) => {
    const feedElem = document.getElementById(data.feedId)
    feedElem.style.opacity = "0";

    setTimeout(() => {
        feedElem.remove();
        isProcessing = false;
    }, 300);
})