const nodes = document.getElementsByClassName('error-label')
for (const error of nodes) {
    error.previousElementSibling.classList.add('error')
}

const password = document.getElementById('password')
const confirm = document.getElementById('confirm')

const errors = Array.from(document.getElementsByClassName('error'))
errors.forEach(e => {
    e.addEventListener('keyup', removeError)
    
});

function removeError(e) {
    console.log()
    if (e.target.classList.contains('error')) {
        e.target.classList.toggle('error')
        e.target.nextElementSibling.remove()

    }
}