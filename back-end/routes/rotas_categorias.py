from fastapi import Form, Depends, HTTPException, APIRouter, Request, Query
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import Categorias, Usuarios
from main import templates

rota_categorias = APIRouter(prefix="/categorias", tags=["categorias"], dependencies=[Depends(verificar_token)])


@rota_categorias.get("/")
async def home(request: Request, usuario: Usuarios = Depends(verificar_token)):
    """
    Essa é a rota padrão das categorias
    """
    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")
    return templates.TemplateResponse(request = request, 
                                      name = "categoria.html")


@rota_categorias.post("/categoria/criar")
async def criar_categoria(categoria: str = Form(...),descricao: str = Form(...), session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):

    existe_categoria = session.query(Categorias).filter(Categorias.categoria == categoria, Categorias.id_usuario == usuario.id).first()
    if existe_categoria:
        raise HTTPException(status_code = 400, detail="Categoria já cadastrada em sistema!")

    nova_categoria = Categorias(id_usuario = usuario.id, categoria = categoria, status_categoria = "ATIVO", descricao = descricao)
    session.add(nova_categoria)
    session.commit()

    return {"mensagem": f"A Categoria {categoria} foi cadastrada com sucesso! "}
    

@rota_categorias.patch("/categoria/editar/{categoria_id}")
async def editar_categoria(categoria_id: int, categoria_titulo: str = Form(...), categoria_descricao: str = Form(...), categoria_status: str = Form(...), session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    categoria = session.query(Categorias).filter(Categorias.id == categoria_id, Categorias.id_usuario == usuario.id).first()
    if not categoria:
        raise HTTPException(status_code = 404, detail = "Não existe essa categoria cadastrada em sistema." )
    if categoria_status not in ["ATIVO", "INATIVO"]:
        raise HTTPException(status_code = 401, detail = "A categoria só pode ser ATIVO ou INATIVO.")
    categoria.categoria = categoria_titulo
    categoria.descricao = categoria_descricao
    categoria.status_categoria = categoria_status
    session.commit()
    return {"mensagem": "A categoria foi alterada com sucesso"}


@rota_categorias.post("/categoria/excluir/{categoria_id}")
async def excluir_categoria(categoria_id: int, session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    categoria = session.query(Categorias).filter(Categorias.id == categoria_id, Categorias.id_usuario == usuario.id).first()

    if not categoria:
        raise HTTPException(status_code = 404, detail = "Não existe essa categoria cadastrada em sistema.")
    
    categoria.status_categoria = "INATIVO"
    session.commit()


@rota_categorias.get("/categoria/listar")
async def listar_categoria(request: Request,
                           session: Session = Depends(pegar_sessao), 
                           usuario: Usuarios = Depends(verificar_token),                        
                           status_categoria: str | None = Form(None)):

    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")
    if status_categoria:
        categorias = session.query(Categorias).filter(Categorias.id_usuario == usuario.id, Categorias.status_categoria == status_categoria).all()
        if not categorias:
            raise HTTPException(status_code = 400, detail = "Não existe categoria cadastrada para este usuário")
    if status_categoria is None:
        categorias = []
        
    return templates.TemplateResponse(
        name="lista_categorias.html", 
        request=request, 
        context={
            "categorias": categorias,
            "usuario": usuario
        }
    )



