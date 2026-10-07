from datetime import datetime, timezone
from typing import Optional 
from sqlmodel import SQLModel, Field 

#modelando a tabela barbearia
class Barbearia(SQLModel, table=True): 
    id: Optional[int] = Field(default=None, primary_key=True) #Optional[int] com default=None no id é porque o banco gera esse valor sozinho (auto-incremento) — nunca vai preencher o id manualmente
    nome: str 
    endereco: Optional[str] = None 
    telefone: Optional[str] = None 
    dono_id: int = Field(foreign_key="usuario.id") #cria o vínculo com a tabela Usuario
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))