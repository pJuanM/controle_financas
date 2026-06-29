from models import db
from fastapi import Depends, HTTPException, Cookie, Request
from sqlalchemy.orm import sessionmaker, Session
from models import Usuarios
from main import SECRET_KEY, ALGORITHM, oauth2_schema
from jose import jwt, JWTError
from main import templates

def pegar_sessao():
    try:
        Session = sessionmaker(bind = db)
        session = Session()
        yield session
    finally:
        session.close()

    
def verificar_token(access_token: str = Cookie(None), session: Session = Depends(pegar_sessao)):
    if not access_token:
        return None
    try:
        dict_info = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = int(dict_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code = 401, detail = "Acesso negado ou expirado.")
    
    usuario = session.query(Usuarios).filter(Usuarios.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code = 401, detail = "Acesso inválido")
    
    
    return usuario