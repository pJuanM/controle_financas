// ESCONDER BOTOES QUANDO SELECIONAR INPUT OU SELECT
const campos = document.querySelectorAll('.menu_editar input, .menu_editar select');
const botoes = document.querySelector(".botoes_formulario");
campos.forEach(campo => {
    if (campo.type === 'hidden') return;

    campo.addEventListener('focus', () => {
        botoes.style.display = 'none';
    });

    campo.addEventListener('blur', () => {
        setTimeout(() => {
            const campoComFoco = [...campos].some(c => c === document.activeElement);
            botoes.style.display = campoComFoco ? 'none' : '';
        }, 0);
    });
});


// ADICIONAR COMPORTAMENTO DE MENU DROPDOWN NO DETAILS DE SELECIONAR PAGADOR RESPONSAVEL
document.addEventListener("click", function(event) {
    const filtros = document.querySelectorAll(".filtroDetails");

    filtros.forEach(function(filtro) {
        if (!filtro.contains(event.target)) {
            filtro.open = false;
        }
    });
});

// POSITION FIXED NO HEADER
const header = document.querySelector("header")

window.addEventListener("scroll", () => {
  if (window.scrollY > 100) {
    header.classList.add("fixed");
  } else {
    header.classList.remove("fixed");
  }
});
