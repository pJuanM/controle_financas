from fastapi import Form, Depends, HTTPException, APIRouter, Request, Query
from fastapi.responses import RedirectResponse
from urllib.parse import quote
from typing import Optional
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import FormasPagamento, Usuarios
from main import templates


rota_home = APIRouter(prefix="/home", tags=["home"], dependencies=[Depends(verificar_token)])


@rota_home.get("/")
async def homepage(request: Request,
                                session: Session = Depends(pegar_sessao), 
                                usuario: Usuarios = Depends(verificar_token)):
    """
    Essa é a rota padrão das formas de pagamentos.
    """
    
    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")
    
    return templates.TemplateResponse(
        request = request,
        name = "home.html"
    )