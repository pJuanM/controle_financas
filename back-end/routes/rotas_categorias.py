from fastapi import Form, Depends, HTTPException, APIRouter, Request
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import Categoria, Usuario
from main import templates

rota_categoria = APIRouter(prefix="/categorias", tags=["categorias"])


@rota_categoria.get("/")
async def home(request: Request, session: Session = Depends(pegar_sessao) ):
    """
    Essa é a rota padrão das categorias
    """
    return templates.TemplateResponse(request= request, 
                                      name = "categoria.html")


@rota_categoria.post("/criarCategoria")
async def criar_categoria(categoria: str = Form(...),descricao: str = Form(...), session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):

    existe_categoria = session.query(Categoria).filter(Categoria.categoria == categoria, Categoria.id_usuario == usuario.id).first()
    if existe_categoria:
        raise HTTPException(status_code = 400, detail="Categoria já cadastrada em sistema!")

    else:
        nova_categoria = Categoria(id_usuario = usuario.id, categoria = categoria, descricao = descricao)
        session.add(nova_categoria)
        session.commit()

        return {"mensagem": f"A Categoria {categoria} foi cadastrada com sucesso! "}
    

@rota_categoria.post("/editarCategoria/{categoria_id}")
async def editar_categoria(categoria_id: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    existeCategoria = session.query(Categoria).filter(Categoria.id == categoria_id, Categoria.id_usuario == usuario.id).first()
    if not existeCategoria:
        raise HTTPException(status_code = 404, detail = "Não existe está categoria cadastrada." )

