from fastapi import APIRouter, Form, Depends, HTTPException, Request
from models import Usuario
from dependencies import pegar_sessao
from sqlalchemy.orm import Session
from main import templates


rota_autenticacao = APIRouter(prefix="/usuario", tags=["usuario"])

@rota_autenticacao.get("/")
async def home(request: Request, session: Session = Depends(pegar_sessao)):
    """
    Essa é a rota padrão de usuários do sistema.
    """

    return templates.TemplateResponse(request= request, name="cadastro.html")

@rota_autenticacao.post("/criarUsuario")
async def criar_usuario(usuario: str = Form(...), nome: str = Form(...), email: str = Form(...), senha: str = Form(...), session: Session = Depends(pegar_sessao)):
    
    existe_usuario = session.query(Usuario).filter(Usuario.email == email).first()

    if existe_usuario:
        raise HTTPException(status_code= 400, detail = "Este e-mail já foi cadastrado em sistema.")
    
    novo_usuario = Usuario(usuario = usuario, nome = nome, email = email, senha = senha)
    session.add(novo_usuario)
    session.commit()


    return {"mensagem" : "Usuário cadastrado com sucesso!"}


@rota_autenticacao.post("/login")
async def login(email: str = Form(...), senha: str = Form(...), session: Session = Depends(pegar_sessao)):
    existe_usuario = session.query(Usuario).filter(Usuario.email == email).first()

    if not existe_usuario:
        raise HTTPException(status_code = 400, detail = "Não existe conta cadastrada para este e-mail.")
    
    if existe_usuario.senha != senha:
        raise HTTPException(status_code = 400, detail = "Senha incorreta!")
    
    return {"mensagem" : "Login realizado com sucesso"}
    
