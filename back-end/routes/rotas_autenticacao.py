from fastapi import APIRouter, Form, Depends, HTTPException, Request
from models import Usuarios
from dependencies import pegar_sessao, verificar_token
from sqlalchemy.orm import Session
from main import templates, ALGORITHM, ACCESS_TOKEN_EXPIRE_HOURS, SECRET_KEY, bcrypt_context
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi.responses import RedirectResponse


# ======= LOGIN VIA FAST API =======
from fastapi.security import OAuth2PasswordRequestForm

rota_autenticacao = APIRouter(prefix="/usuario", tags=["usuario"])

def criar_token(usuario_id, 
                duracao_token =  timedelta(hours = ACCESS_TOKEN_EXPIRE_HOURS)):
    

    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dict_info = {"sub": str(usuario_id), "exp": data_expiracao}
    jwt_codificado = jwt.encode(dict_info, SECRET_KEY, ALGORITHM)

    return jwt_codificado


def autenticar_usuario(nome_usuario, 
                       senha, 
                       session):
    
    nome_usuario = nome_usuario.upper()
    existe_usuario = session.query(Usuarios).filter(Usuarios.email == nome_usuario).first()
    if not existe_usuario:
        existe_usuario = session.query(Usuarios).filter(Usuarios.usuario == nome_usuario).first()
        if not existe_usuario:
            raise HTTPException(status_code= 400, detail = "Não tem usuário cadastrado para este e-mail!")
    if not bcrypt_context.verify(senha, existe_usuario.senha):
        raise HTTPException(status_code= 400, detail="Senha incorreta")

    return existe_usuario


@rota_autenticacao.get("/cadastro")
async def home(request: Request):
    """
    Essa é a rota padrão de usuários do sistema.
    """
    return templates.TemplateResponse(request = request, name="cadastro.html")

@rota_autenticacao.post("/cadastro/criar")
async def criar_usuario(usuario: str = Form(...), 
                        nome: str = Form(...), 
                        email: str = Form(...), 
                        senha: str = Form(...), 
                        session: Session = Depends(pegar_sessao)):
    
    # === PASSANDO CADASTRO EM UPPERCASE ===
    usuario = usuario.upper()
    nome = nome.upper()
    email = email.upper()
    
    existe_usuario = session.query(Usuarios).filter(Usuarios.email == email).first()
    if existe_usuario:
        raise HTTPException(status_code= 400, detail = "Este e-mail já foi cadastrado em sistema.")
    senha_criptografada = bcrypt_context.hash(senha)
    novo_usuario = Usuarios(usuario = usuario, nome = nome, status_usuario = "ATIVO", email = email, senha = senha_criptografada)
    session.add(novo_usuario)
    session.commit()


    return RedirectResponse(
        url = "/usuario/login",
        status_code = 303
    )


@rota_autenticacao.get("/login")
async def login(request: Request):
    """
    Essa é a rota para carregar o html da página
    """
    return templates.TemplateResponse(request = request, name = "login.html")


@rota_autenticacao.post("/login")
async def login(nome_usuario: str = Form(...), 
                senha: str = Form(...), 
                session: Session = Depends(pegar_sessao)):
    
    nome_usuario = nome_usuario.upper()
    
    usuario = autenticar_usuario(nome_usuario, senha, session)
    access_token = criar_token(usuario.id)
    response = RedirectResponse(
        url="/home",
        status_code = 303
    )

    response.set_cookie(
        key = "access_token",
        value = access_token,
        httponly=True
    )

    return response


@rota_autenticacao.get("/refresh")
async def use_refresh_token(usuario: Usuarios = Depends(verificar_token)):

    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }
        

@rota_autenticacao.get("/logout")
async def logout():
    response = RedirectResponse(
        url = "/usuario/login",
        status_code= 303
    )
    response.delete_cookie("access_token")

    return response
