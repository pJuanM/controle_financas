const senha = document.getElementById("senha");
const confirmeSenha = document.getElementById("confirme_senha");
const erro = document.getElementById("erroSenha");

confirmeSenha.addEventListener("input", () => {
    if (senha.value !== confirmeSenha.value) {
        erro.textContent = "As senhas não coincidem.";
    } else {
        erro.textContent = "";
    }
});


document.getElementById("formulario").addEventListener("submit", function(event) {
    if (senha.value != confirmeSenha.value) {
        event.preventDefault;
        erro.textContent = "As senhas não coincidem.";
    } else {
        erro.textContent = "";
    }

})