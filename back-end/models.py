from sqlalchemy import  create_engine, Column, Boolean, Integer, String, ForeignKey, Date, Float, Numeric
from sqlalchemy.orm import declarative_base, relationship

# ======= CRIAR CONEXÃO COM BANCO DE DADOS =======
db = create_engine("sqlite:///database/banco.db")

# ======= CRIAR BASE DO BANCO DE DADOS =======
Base = declarative_base()

# ======= CRIAR COLUNAS/CLASSES BANCO DE DADOS =======
# ======= LANÇAMENTOS  ======= 
class Lancamentos(Base):
    __tablename__ = "lancamentos" 
    id = Column(Integer, primary_key=True, autoincrement=True) 
    data_compra = Column(Date, nullable=False) 
    item_comprado = Column(String(150), nullable=False) 
    valor_lancamento = Column(Numeric(10, 2), nullable = False)
    parcelado = Column(Boolean, nullable=False) 
    pagador_responsavel = Column(String, nullable=True)
    qnt_parcelas = Column(Integer) 

    id_usuario = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuarios", back_populates="lancamento")

    id_forma_pagamento = Column(Integer, ForeignKey("formasPagamento.id"), nullable=False) 
    formaPagamento = relationship("FormasPagamento", back_populates="lancamento")
    
    id_categoria = Column(Integer, ForeignKey("categorias.id"), nullable=False) 
    categoria = relationship("Categorias", back_populates="lancamento")

    parcela = relationship("Parcelas", back_populates="lancamento", cascade="all, delete-orphan")


# ======= FORMAS DE PAGAMENTO ======= 
class FormasPagamento(Base): 
    __tablename__ = "formasPagamento" 
    id = Column(Integer, primary_key=True, autoincrement=True)  
    forma_pagamento = Column(String(40), nullable=False) 
    responsavel = Column(String(150), nullable=False) 
    data_vencimento = Column(Integer, nullable=True) 
    data_fechamento = Column(Integer, nullable=True)
    status_forma_pagamento = Column(String, nullable=False)

    id_usuario = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuarios", back_populates="forma_pagamento")
    lancamento = relationship("Lancamentos", back_populates="formaPagamento")


# ======= CATEGORIAS ======= 
class Categorias(Base):
    __tablename__ = "categorias" 
    id = Column(Integer, primary_key=True, autoincrement=True) 
    categoria = Column(String(50), nullable=False) 
    descricao = Column(String(100), nullable=False)
    status_categoria = Column(String, nullable=False) 

    id_usuario = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuarios", back_populates="categoria")
    lancamento = relationship("Lancamentos", back_populates="categoria")


# ======= USUÁRIOS ======= 
class Usuarios(Base): 
    __tablename__ = "usuarios" 
    id = Column(Integer, primary_key=True, autoincrement=True) 
    usuario = Column(String(100), nullable=False) 
    nome = Column(String(150), nullable=False) 
    email = Column(String(150), nullable=False) 
    senha = Column(String(16), nullable=False) 
    status_usuario = Column(String, nullable=False)

    categoria = relationship("Categorias", back_populates= "usuario", cascade= "all, delete-orphan")
    forma_pagamento = relationship("FormasPagamento", back_populates= "usuario", cascade= "all, delete-orphan")
    lancamento = relationship("Lancamentos", back_populates="usuario", cascade="all, delete-orphan")


# ======= PARCELAS =======
class Parcelas(Base):
    __tablename__ = "parcelas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_parcela = Column(Integer, nullable=False)
    data_vencimento = Column(Date, nullable= False)
    status_parcela = Column(String, default="PENDENTE", nullable=False)
    valor_parcela = Column(Numeric(10, 2), nullable = False)
    tipo_lancamento = Column(String, nullable=False)

    id_lancamento = Column(Integer, ForeignKey("lancamentos.id"))
    lancamento = relationship("Lancamentos", back_populates="parcela")


Base.metadata.create_all(db)
