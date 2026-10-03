from typing import Optional 
from sqlmodel import SQLModel, Field 

#modelanddo a tabela categoraia financeira
class CategoriaFinanceira(SQLModel, table=True): 
    id: Optional[int] = Field(default=None, primary_key=True) #Optional[int] com default=None no id é porque o banco gera esse valor sozinho (auto-incremento) — nunca vai preencher o id manualmente
    barbearia_id: int = Field(foreign_key="barbearia.id") 
    nome: str 
    tipo: str #"receita" ou "despesa"