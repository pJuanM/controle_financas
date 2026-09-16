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


// EXCLUIR USUÁRIO
const excluirUsuario = document.getElementById("btn_excluir");
const formularioExcluirUsuario = document.getElementById("formulario_usuario");

excluirUsuario.addEventListener("click", async function(event) {

    event.preventDefault();
    const dadosFormularioExcluirUsuario = new FormData(formularioExcluirUsuario);
    const confirmarExcluirUsuario = confirm("Deseja realmente excluir o usuário: ")
    if (confirmarExcluirUsuario == true) {
        try {
            const resposta = await fetch(formularioExcluirUsuario.action, {
                method: "POST",
                body: dadosFormularioExcluirUsuario,
            });

            const dados = await resposta.json();

            if (dados.sucesso) {
                alert(dados.mensagem)
            } else {
                alert(dados.mensagem)
            }
        } catch (erro){
            console.error("Erro na requisição:", erro);
            alert("Ocorreu um erro ao tentar excluir o usuário.");
        }   
    } else {
        alert("Usuário permanece ATIVO!")
    }
    
});

