document.querySelectorAll(".navegar_rotas_menu").forEach(menu => {
    menu.addEventListener("click", () => {
        menu.querySelector(".navegar_rotas_secao").classList.toggle("ativo");
        let elemento = menu.nextElementSibling;

        while (elemento && elemento.classList.contains("navegar_rotas_submenu")) {
            elemento.classList.toggle("ativo")
            elemento = elemento.nextElementSibling;
        };
    });
});


const menu_hamburguer = document.querySelector(".menu_hamburguer")
const fechar_menu_lateral = document.querySelector("#fechar_menu_lateral")
menu_hamburguer.addEventListener("click", () => {
    document.querySelector(".menu_lateral_navegacao").classList.toggle("ativo");
});

fechar_menu_lateral.addEventListener("click", () => {
    document.querySelector(".menu_lateral_navegacao").classList.remove("ativo");
})