const menu = document.getElementById('menu');
const toggle = document.querySelector('.toggle');

toggle.onclick = () => {
    menu.classList.toggle('active');
}