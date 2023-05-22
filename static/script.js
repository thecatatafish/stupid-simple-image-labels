let currentImage = ""
let remainingImages = 0

function getImageElement() {
    return document.getElementById("mainImage");
}

function getRemainingCounter() {
    return document.getElementById("remainingCounter");
}

async function storeCheckpoint() {
    await fetch("/label/checkpoint/", {method: "POST", headers: {"Content-Type": "application/json"}})
}





// getNextImage()
// https://www.freecodecamp.org/news/javascript-keycode-list-keypress-event-key-codes/