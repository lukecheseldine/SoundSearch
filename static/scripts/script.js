// if any alerts, make the close button functional
const closeAlertButtons = document.getElementsByClassName('close')
for (let button of closeAlertButtons) {
    button.addEventListener('click', (e) => {
        e.target.parentNode.remove()
    })
}