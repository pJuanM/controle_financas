from sqlalchemy import text
from models import db

with db.begin() as conn:
    conn.execute(text("""
        ALTER TABLE parcelas
        DROP COLUMN tipo_lancamento;
    """))

print("Coluna removida com sucesso!")