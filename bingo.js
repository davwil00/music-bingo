function toggle(e) {
    e.currentTarget.classList.toggle('crossed')
}

Array.from(document.querySelectorAll('.cell'))
    .forEach(elt => elt.addEventListener('click', toggle))