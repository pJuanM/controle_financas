const novaSenha = document.getElementById("nova_senha");
const confirmeNovaSenha = document.getElementById("confirme_nova_senha");
const erro = document.getElementById("erroSenha");

confirmeNovaSenha.addEventListener("input", () => {
    if (novaSenha.value !== confirmeNovaSenha.value) {
        erro.textContent = "As senhas não coincidem.";
    } else {
        erro.textContent = "";
    }
});


document.getElementById("formulario").addEventListener("submit", function(event) {
    if (novaSenha.value != confirmeNovaSenha.value) {
        event.preventDefault();
        erro.textContent = "As senhas não coincidem.";
    } else {
        erro.textContent = "";
    }

})
