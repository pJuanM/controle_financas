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
        event.preventDefault();
        erro.textContent = "As senhas não coincidem.";
    } else {
        erro.textContent = "";
    }

})


async function login() {
    const formData = new FormData();

    formData.append("email", "teste@email.com");
    formData.append("senha", "123456");

    const resposta = await fetch("http://127.0.0.1:8000/usuario/login", {
        method: "POST",
        body: formData
    });

    const dados = await resposta.json();

    // salva o token
    localStorage.setItem("access_token", dados.access_token);
    localStorage.setItem("refresh_token", dados.refresh_token);

    console.log(dados);
}


const token = localStorage.getItem("access_token");

fetch("http://localhost:8000/debitos", {
    headers: {
        Authorization: `Bearer ${token}`
    }
});