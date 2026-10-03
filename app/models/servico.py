from typing import Optional 
from sqlmodel import SQLModel, Field 

#modelando a tabela serviço
class Servico(SQLModel, table=True): 
    id: Optional[int] = Field(default=None, primary_key=True) #Optional[int] com default=None no id é porque o banco gera esse valor sozinho (auto-incremento) — nunca vai preencher o id manualmente
    barbearia_id: int = Field(foreign_key="barbearia.id") 
    nome: str 
    descricao: Optional[str] = None 
    preco: float #Usei float para preço por simplicidade no MVP. Numa versão mais rigorosa (dinheiro de verdade) vamos trocar por Decimal
    duracao_minutos: int = Field(default=30) 
    ativo: bool = Field(default=True)