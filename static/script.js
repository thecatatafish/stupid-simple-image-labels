let currentImage = ""
let remainingImages = 0

function getImageElement() {
    return document.getElementById("mainImage");
}

function getRemainingCounter() {
    return document.getElementById("remainingCounter");
}

async function storeLabel(labelValue, imageName) {
    let response = await fetch("/label/", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"label": labelValue, "image": imageName})
    })
}

async function storeCheckpoint() {
    await fetch("/label/checkpoint/", {method: "POST", headers: {"Content-Type": "application/json"}})
}

async function getNextImage() {
    await fetch("/image/").then(response => {
        if (response.ok) {
            return response.json()
        }
    }).then(data => {
        let mainImageElement = getImageElement()
        mainImageElement.src = data.src
        currentImage = data.src
        remainingImages = data.numImagesRemaining
        getRemainingCounter().innerHTML = remainingImages
        if (remainingImages === 0) {
            document.getElementById("buttonContainer").style.display = 'none'
        }
    })

}

async function storeAndGetNext(labelValue, imageName) {
    storeLabel(labelValue, currentImage)
    getNextImage()
}

getNextImage()
// https://www.freecodecamp.org/news/javascript-keycode-list-keypress-event-key-codes/