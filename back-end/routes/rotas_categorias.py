from typing import Optional
from urllib.parse import quote

from dependencies import pegar_sessao, verificar_token
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from main import templates
from models import Categorias, Usuarios
from sqlalchemy.orm import Session

rota_categorias = APIRouter(prefix="/categorias", tags=["categorias"], dependencies=[Depends(verificar_token)])

@rota_categorias.get("/")
async def listar_categoria(request: Request,
                           session: Session = Depends(pegar_sessao), 
                           usuario: Usuarios = Depends(verificar_token),                        
                           status_categoria: str | None = Query(None)):
    """
    Essa é a rota padrão das categorias
    """

    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")
    
    filtros_aplicados = any([
        status_categoria
    ])
    categorias = []

    if filtros_aplicados:
        categorias = session.query(Categorias).filter(Categorias.id_usuario == usuario.id, Categorias.status_categoria == status_categoria).all()
        
    return templates.TemplateResponse(
        name="lista_categorias.html", 
        request=request, 
        context={
            "categorias": categorias,
            "usuario": usuario,
            "status_categoria": status_categoria
        }
    )


@rota_categorias.get("/criar")
async def home(request: Request,
               mensagem: Optional[str] = None, 
               usuario: Usuarios = Depends(verificar_token)):
    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")
    return templates.TemplateResponse(request = request, 
                                      name = "categoria.html",
                                      context={
                                          "mensagem": mensagem
                                      })


@rota_categorias.post("/criar")
async def criar_categoria(categoria: str = Form(...),
                          descricao: str = Form(...), 
                          session: Session = Depends(pegar_sessao), 
                          usuario: Usuarios = Depends(verificar_token)):


    existe_categoria = session.query(Categorias).filter(
        Categorias.categoria == categoria.upper(), 
        Categorias.id_usuario == usuario.id).first()
    
    if existe_categoria:
        return {
            "sucesso": False,
            "mensagem": "Categoria já cadastrada em sistema."
        }
    
    nova_categoria = Categorias(id_usuario = usuario.id, 
                                categoria = categoria.upper(), 
                                status_categoria = "ATIVO", 
                                descricao = descricao.upper())
    session.add(nova_categoria)
    session.commit()
    
    return {
        "sucesso": True,
        "mensagem": "Categoria cadastrada com sucesso!" 
    }
    

@rota_categorias.post("/editar")
async def editar_categoria(categoria_id: int = Form(...), 
                           categoria_titulo: str | None = Form(None), 
                           categoria_descricao: str | None = Form(None), 
                           categoria_status: str | None = Form(None), 
                           session: Session = Depends(pegar_sessao), 
                           usuario: Usuarios = Depends(verificar_token)):
    

    categoria = session.query(Categorias).filter(
        Categorias.id == categoria_id, 
        Categorias.id_usuario == usuario.id).first()
    
    if not categoria:
        return {
            "sucesso": False,
            "mensagem": "Categoria não existe ou INATIVA."
        }

    if categoria_titulo:
        categoria_existente = session.query(Categorias).filter(
            Categorias.categoria == categoria_titulo.upper(),
            Categorias.id_usuario == usuario.id,
            Categorias.id != categoria_id
        ).first()
        if categoria_existente:
            return {
                "sucesso": False,
                "mensagem": "Já existe uma categoria com este nome."
            }
    
    if categoria_status not in ["ATIVO", "INATIVO"]:
        return {
            "sucesso": False,
            "mensagem": "A categoria só pode ser ATIVO ou INATIVO."
        }
    
    categoria.categoria = categoria_titulo.upper()
    categoria.descricao = categoria_descricao.upper()
    categoria.status_categoria = categoria_status.upper()
    session.commit()

    return {
        "sucesso": True,
        "mensagem": "Categoria editada com sucesso!",
        "categoria": categoria.categoria,
        "descricao": categoria.descricao,
        "status_categoria": categoria.status_categoria
    }


@rota_categorias.post("/excluir")
async def excluir_categoria(categoria_id: int = Form(...), 
                            session: Session = Depends(pegar_sessao), 
                            usuario: Usuarios = Depends(verificar_token)):
    

    categoria = session.query(Categorias).filter(Categorias.id == categoria_id, Categorias.id_usuario == usuario.id).first()

    if not categoria:
        return {
            "sucesso": False,
            "mensagem": "Categoria não existe ou INATIVA."
        }
    
    categoria.status_categoria = "INATIVO"
    session.commit()

    return {
        "sucesso": True,
        "mensagem": "Categoria inativada com sucesso!"
    }





