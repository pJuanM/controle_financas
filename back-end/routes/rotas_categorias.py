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


@rota_categoria.post("/categoria/criar")
async def criar_categoria(categoria: str = Form(...),descricao: str = Form(...), session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):

    existe_categoria = session.query(Categoria).filter(Categoria.categoria == categoria, Categoria.id_usuario == usuario.id).first()
    if existe_categoria:
        raise HTTPException(status_code = 400, detail="Categoria já cadastrada em sistema!")

    else:
        nova_categoria = Categoria(id_usuario = usuario.id, categoria = categoria, status_categoria = "ATIVO", descricao = descricao)
        session.add(nova_categoria)
        session.commit()

        return {"mensagem": f"A Categoria {categoria} foi cadastrada com sucesso! "}
    

@rota_categoria.patch("/categoria/editar/{categoria_id}")
async def editar_categoria(categoria_id: int, categoria_titulo: str = Form(...), categoria_descricao: str = Form(...), session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    categoria = session.query(Categoria).filter(Categoria.id == categoria_id, Categoria.id_usuario == usuario.id).first()
    if not categoria:
        raise HTTPException(status_code = 404, detail = "Não existe essa categoria cadastrada em sistema." )

    categoria.categoria = categoria_titulo
    categoria.descricao = categoria_descricao
    session.commit()
    return {"mensagem": "A categoria foi alterada com sucesso"}


@rota_categoria.post("/categoria/excluir/{categoria_id}")
async def excluir_categoria(categoria_id: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    categoria = session.query(Categoria).filter(Categoria.id == categoria_id, Categoria.id_usuario == usuario.id).first()

    if not categoria:
        raise HTTPException(status_code = 404, detail = "Não existe essa categoria cadastrada em sistema.")
    
    categoria.status_categoria = "CANCELADO"
    session.commit()