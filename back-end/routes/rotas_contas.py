from fastapi import APIRouter, Form, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import ContasPagar, Categoria, FormaPagamento, Usuario
from main import templates
from decimal import Decimal
from datetime import date


rota_conta = APIRouter(prefix="/contasPagar", tags=["conta"])

@rota_conta.get("/")
async def home(request: Request, session: Session = Depends(pegar_sessao)):
    """
    Essa é a rota padrão das contas.
    """
    categorias = session.query(Categoria).all()
    formas_pagamento = session.query(FormaPagamento).all()


    return templates.TemplateResponse(
        name="contas_a_pagar.html", 
        request=request, 
        context={
            "categorias": categorias,
            "formas_pagamento": formas_pagamento
        }
    )

@rota_conta.post("/criarConta")
async def criar_conta(data_compra: date = Form(...), 
                      item_comprado: str = Form(...), 
                      categoria_id: int = Form(...),  
                      forma_pagamento: int = Form(...), 
                      status_conta: str = "Pendente",
                      valor_debito: str = Form(...),
                      parcelado: bool = Form(...), 
                      qnt_parcelas: int | None = Form(None), 
                      session: Session = Depends(pegar_sessao), 
                      usuario: Usuario = Depends(verificar_token)):
    valor_debito = (valor_debito.replace("R$", "").replace(".", "").replace(",", ".").strip())
    valor_debito = Decimal(valor_debito)
    existeConta = session.query(ContasPagar).filter(ContasPagar.data_compra == data_compra, 
                                                    ContasPagar.id_usuario == usuario.id,
                                                    ContasPagar.item_comprado == item_comprado, 
                                                    ContasPagar.forma_pagamento == forma_pagamento).first()

    if parcelado == False:
        qnt_parcelas = None
    else:
        if qnt_parcelas == None or qnt_parcelas <= 0 :
            raise HTTPException(status_code = 400, detail = "A quantidade de parcelas precisa ser maior do que 0.")

    if existeConta:
        return {"mensagem": "Compra adicionada com sucesso. = Já existe uma compra idêntica em sistema, por gentileza analise."}
    
    novaConta = ContasPagar(data_compra = data_compra, id_usuario = usuario.id, status_conta = status_conta , item_comprado = item_comprado, categoria_id = categoria_id, forma_pagamento = forma_pagamento, valor_debito = valor_debito, parcelado = parcelado, qnt_parcelas = qnt_parcelas)
    session.add(novaConta)
    session.commit()


    return {"mensagem": "Compra adicionada com sucesso!"}


@rota_conta.post("/deletarConta/{id_conta}")
async def deletar_conta(id_conta: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    conta = session.query(ContasPagar).filter(ContasPagar.id == id_conta).first()

    if not conta:
        raise HTTPException(status_code = 400, detail = "Conta não encontrada em sistema")
    
    if usuario.id != conta.id_usuario:
        raise HTTPException(status_code = 401, detail = "Usuário não tem permissão para excluir esta conta.")  
    
    session.delete(conta)
    session.commit

    return {"mensagem": f"Conta excluída com sucesso! - ID da conta {conta.id}",
            "conta": conta}


@rota_conta.get("/listarContas")
async def listar_contas(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedidos = session.query(ContasPagar).filter(ContasPagar.id_usuario == usuario.id).all()
    return {
        "pedidos": pedidos
    }