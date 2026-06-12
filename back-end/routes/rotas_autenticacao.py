from fastapi import APIRouter, Form, Depends, HTTPException, Request
from models import Usuario
from dependencies import pegar_sessao, verificar_token
from sqlalchemy.orm import Session
from main import templates, ALGORITHM, ACCESS_TOKEN_EXPIRE_HOURS, SECRET_KEY
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

# ======= LOGIN VIA FAST API =======
from fastapi.security import OAuth2PasswordRequestForm

rota_autenticacao = APIRouter(prefix="/usuario", tags=["usuario"])

def criar_token(usuario_id, duracao_token =  timedelta(hours = ACCESS_TOKEN_EXPIRE_HOURS)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dict_info = {"sub": str(usuario_id), "exp": data_expiracao}
    jwt_codificado = jwt.encode(dict_info, SECRET_KEY, ALGORITHM)

    return jwt_codificado


def autenticar_usuario(email, senha, session):
    existe_usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not existe_usuario:
        raise HTTPException(status_code= 400, detail = "Não tem usuário cadastrado para este e-mail!")
    if senha != existe_usuario.senha:
        raise HTTPException(status_code= 400, detail="Senha incorreta")
    return existe_usuario


@rota_autenticacao.get("/")
async def home(request: Request):
    """
    Essa é a rota padrão de usuários do sistema.
    """
    return templates.TemplateResponse(request = request, name="cadastro.html")

@rota_autenticacao.post("/criarUsuario")
async def criar_usuario(usuario: str = Form(...), nome: str = Form(...), email: str = Form(...), senha: str = Form(...), session: Session = Depends(pegar_sessao)):
    existe_usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if existe_usuario:
        raise HTTPException(status_code= 400, detail = "Este e-mail já foi cadastrado em sistema.")
    novo_usuario = Usuario(usuario = usuario, nome = nome, email = email, senha = senha)
    session.add(novo_usuario)
    session.commit()


    return {"mensagem" : "Usuário cadastrado com sucesso!"}


@rota_autenticacao.get("/login")
async def login(request: Request):
    """
    Essa é a rota para carregar o html da página
    """
    return templates.TemplateResponse(request = request, name = "login.html")

@rota_autenticacao.post("/login")
async def login(email: str = Form(...), senha: str = Form(...), session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(email, senha, session)
    access_token = criar_token(usuario.id)
    refresh_token = criar_token(usuario.id, duracao_token = timedelta(days = 7))
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }

# ======= LOGIN VIA FAST API =======
@rota_autenticacao.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }



@rota_autenticacao.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }
        