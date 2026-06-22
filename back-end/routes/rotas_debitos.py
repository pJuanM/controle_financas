from fastapi import APIRouter, Form, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import Debitos, Categoria, FormasPagamento, Usuario
from main import templates
from decimal import Decimal
from datetime import date


rota_debito = APIRouter(prefix="/debitos", tags=["debitos"])

@rota_debito.get("/")
async def home(request: Request, session: Session = Depends(pegar_sessao)):
    """
    Essa é a rota padrão das contas.
    """
    categorias = session.query(Categoria).all()
    formas_pagamento = session.query(FormasPagamento).all()


    return templates.TemplateResponse(
        name="debitos.html", 
        request=request, 
        context={
            "categorias": categorias,
            "formas_pagamento": formas_pagamento
        }
    )

@rota_debito.post("/criar")
async def criar_debito(data_compra: date = Form(...), 
                      item_comprado: str = Form(...), 
                      categoria_id: int = Form(...),  
                      forma_pagamento: int = Form(...), 
                      valor_debito: str = Form(...),
                      parcelado: bool = Form(...), 
                      qnt_parcelas: int | None = Form(None), 
                      session: Session = Depends(pegar_sessao), 
                      usuario: Usuario = Depends(verificar_token)):
    valor_debito = (valor_debito.replace("R$", "").replace(".", "").replace(",", ".").strip())
    valor_debito = Decimal(valor_debito)
    existeConta = session.query(Debitos).filter(Debitos.data_compra == data_compra, 
                                                    Debitos.id_usuario == usuario.id,
                                                    Debitos.item_comprado == item_comprado, 
                                                    Debitos.forma_pagamento == forma_pagamento).first()

    if parcelado == False:
        qnt_parcelas = None
    else:
        if qnt_parcelas == None or qnt_parcelas <= 0 :
            raise HTTPException(status_code = 400, detail = "A quantidade de parcelas precisa ser maior do que 0.")

    if existeConta:
        return {"mensagem": "Compra adicionada com sucesso. - Já existe uma compra idêntica em sistema, por gentileza analise."}
    
    novaConta = Debitos(data_compra = data_compra, id_usuario = usuario.id, status_debito = "PENDENTE" , item_comprado = item_comprado, categoria_id = categoria_id, forma_pagamento = forma_pagamento, valor_debito = valor_debito, parcelado = parcelado, qnt_parcelas = qnt_parcelas)
    session.add(novaConta)
    session.commit()


    return {"mensagem": "Compra adicionada com sucesso!"}


@rota_debito.patch("/editar")
async def editar_debito(id_debito: int,
                        item_comprado: str | None = Query(None),
                        categoria_id: int | None = Query(None),
                        forma_pagamento: int | None = Query(None),
                        valor_debito: str | None = Query(None),
                        parcelado: bool | None = Query(None),
                        qnt_parcelas: int | None = Query(None),
                        status_debito : str | None = Query(None),
                        session: Session = Depends(pegar_sessao), 
                        usuario: Usuario = Depends(verificar_token)):
    
    debito = session.query(Debitos).filter(Debitos.id == id_debito, Debitos.id_usuario == usuario.id).first()
    if not debito:
        raise HTTPException(status_code = 400, detail = "Débito não cadastrado")
    
    if item_comprado is not None:
        debito.item_comprado = item_comprado
    
    if categoria_id is not None:
        debito.categoria_id = categoria_id

    if forma_pagamento is not None:
        debito.forma_pagamento = forma_pagamento
    
    if valor_debito is not None:
        valor_debito = (valor_debito.replace("R$", "").replace(".", "").replace(",", ".").strip())
        debito.valor_debito = Decimal(valor_debito)

    if parcelado is not None:
        debito.parcelado = parcelado

    if qnt_parcelas is not None:
        debito.qnt_parcelas = qnt_parcelas

    if status_debito is not None:
        if status_debito not in ["PENDENTE", "CANCELADO", "PAGO"]:
            raise HTTPException(status_code = 400, detail = "O status do débito precisa ser: 'PENDENTE', 'CANCELADO' ou 'PAGO'")
        debito.status_debito = status_debito
    
    session.commit()

    return {"mensagem": "Débito alterado com sucesso!"}
     



@rota_debito.post("/cancelar/{id_debito}")
async def deletar_conta(id_debito: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    conta = session.query(Debitos).filter(Debitos.id == id_debito).first()

    if not conta:
        raise HTTPException(status_code = 400, detail = "Conta não encontrada em sistema")
    
    if usuario.id != conta.id_usuario:
        raise HTTPException(status_code = 401, detail = "Usuário não tem permissão para excluir esta conta.")  
    
    conta.status_debito = "CANCELADO"
    session.commit()

    return {"mensagem": f"Conta excluída com sucesso! - ID da conta {conta.id}",
            "conta": conta}


@rota_debito.get("/listar")
async def listar_contas(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    debitos = session.query(Debitos).filter(Debitos.id_usuario == usuario.id).all()
    return {
        "debitos": debitos
    }