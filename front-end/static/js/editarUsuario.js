// ABRIR OVERLAY
// PEGAR ELEMENTOS .MENU_EDITAR E .OVERLAY 
function abrirEdicaoUsuario() {
    const menu_editar = document.querySelector(".menu_editar");
    const overlay = document.querySelector(".overlay")
    if (!menu_editar || !overlay) {
        console.error("Menu de edição ou overlay não encontrado.");
        return;
    }
    // ABRIR MENU
    menu_editar.classList.add("ativo");
    overlay.classList.add("ativo");
    // FECHAR MENU
    function fecharMenu() {
        menu_editar.classList.remove("ativo");
        overlay.classList.remove("ativo");
    }
    // FECHAR AO CLICAR NO OVERLAY
    overlay.addEventListener("click", fecharMenu, { 
        once: true 
    });
    // ADICIONAR EVENTO DE FECHAR O MENU QUANDO PRESSIONAR O BOTAO ESCAPE BASEADO NO EVENTO REALIZADO
    addEventListener("keydown", function(e) {
        if (e.key === "Escape" && menu_editar.classList.contains("ativo")) {
            fecharMenu() ;
        }   
    })
}

