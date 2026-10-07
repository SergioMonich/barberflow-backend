from datetime import datetime, timezone 
from typing import Optional 
from sqlmodel import SQLModel, Field 

#modelandio tabela financeiro
class MovimentacaoFinanceira(SQLModel, table=True): 
    id: Optional[int] = Field(default=None, primary_key=True) #Optional[int] com default=None no id é porque o banco gera esse valor sozinho (auto-incremento) — nunca vai preencher o id manualmente
    barbearia_id: int = Field(foreign_key="barbearia.id") 
    tipo: str # "receita" ou "despesa" 
    categoria_id: int = Field(foreign_key="categoriafinanceira.id") 
    descricao: Optional[str] = None 
    valor: float
    #"""MovimentacaoFinanceira.valor precisa existir de forma independente porque nem toda movimentação vem de um agendamento. Uma despesa de aluguel, por exemplo, não tem agendamento nenhum por trás, então não tem de onde "puxar" um valor. Nesse caso, valor é o único lugar onde esse número existe. Quando a movimentação vem de um agendamento concluído (receita automática), valor vai ser preenchido copiando o Agendamento.valor daquele momento.""" 
    data: datetime 
    agendamento_id: Optional[int] = Field(default=None, foreign_key="agendamento.id") 
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))