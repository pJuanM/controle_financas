from fastapi import APIRouter, Form, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from dependencies import pegar_sessao
from models import ContasPagar, Categoria, FormaPagamento
from main import templates  
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
                      parcelado: bool = Form(...), 
                      qnt_parcelas: int | None = Form(None) , 
                      session: Session = Depends(pegar_sessao)):
    existeConta = session.query(ContasPagar).filter(ContasPagar.data_compra == data_compra, ContasPagar.item_comprado == item_comprado, ContasPagar.forma_pagamento == forma_pagamento).first()
    if existeConta:
        raise HTTPException(status_code = 400, detail = "Esta compra já foi incluída.")

    if parcelado == False:
        qnt_parcelas = None
    else:
        if qnt_parcelas == None or qnt_parcelas <= 0 :
            raise HTTPException(status_code = 400, detail = "A quantidade de parcelas precisa ser maior do que 0.")

    novaConta = ContasPagar(data_compra = data_compra, item_comprado = item_comprado, categoria_id = categoria_id, forma_pagamento = forma_pagamento, parcelado = parcelado, qnt_parcelas = qnt_parcelas)
    session.add(novaConta)
    session.commit()

    return {"mensagem": "Compra adicionada com sucesso!"}
