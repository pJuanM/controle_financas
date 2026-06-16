from sqlalchemy import  create_engine, Column, Boolean, Integer, String, ForeignKey, Date, Float, Numeric
from sqlalchemy.orm import declarative_base

# ======= CRIAR CONEXÃO COM BANCO DE DADOS =======
db = create_engine("sqlite:///database/banco2.db")

# ======= CRIAR BASE DO BANCO DE DADOS =======
Base = declarative_base()

# ======= CRIAR COLUNAS/CLASSES BANCO DE DADOS =======
# ======= CONTAS À PAGAR ======= 
class ContasPagar(Base):
    __tablename__ = "contasPagar" 
    id = Column(Integer, primary_key=True, autoincrement=True) 
    id_usuario = Column(Integer, ForeignKey("usuario.id"))
    data_compra = Column(Date, nullable=False) 
    item_comprado = Column(String(150), nullable=False) 
    categoria_id = Column(Integer, ForeignKey("categoria.id"), nullable=False) 
    forma_pagamento = Column(Integer, ForeignKey("formaPagamento.id"), nullable=False) 
    valor_debito = Column(Numeric(10, 2), nullable = False)
    parcelado = Column(Boolean, nullable=False) 
    status_conta = Column(String, nullable=False)
    qnt_parcelas = Column(Integer) 
    
# ======= FORMA DE PAGAMENTO ======= 
class FormaPagamento(Base): 
    __tablename__ = "formaPagamento" 
    id = Column(Integer, primary_key=True, autoincrement=True)  
    id_usuario = Column(Integer, ForeignKey("usuario.id"))
    forma_pagamento = Column(String(40), nullable=False) 
    responsavel = Column(String(150), nullable=False) 
    vencimento = Column(Boolean, nullable=False) 
    data_vencimento = Column(Integer) 

    
# ======= CATEGORIA ======= 
class Categoria(Base):
    __tablename__ = "categoria" 
    id = Column(Integer, primary_key=True, autoincrement=True) 
    id_usuario = Column(Integer, ForeignKey("usuario.id"))
    categoria = Column(String(50), nullable=False) 
    descricao = Column(String(100), nullable=False) 
        
    
# ======= USUÁRIO ======= 
class Usuario(Base): 
    __tablename__ = "usuario" 
    id = Column(Integer, primary_key=True, autoincrement=True) 
    usuario = Column(String(100), nullable=False) 
    nome = Column(String(150), nullable=False) 
    email = Column(String(150), nullable=False) 
    senha = Column(String(16), nullable=False) 


Base.metadata.create_all(db)
