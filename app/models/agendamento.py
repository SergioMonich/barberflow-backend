from datetime import datetime, timezone 
from typing import Optional 
from sqlmodel import SQLModel, Field 

#modelando tabela agendamento
class Agendamento(SQLModel, table=True): 
    id: Optional[int] = Field(default=None, primary_key=True) #Optional[int] com default=None no id é porque o banco gera esse valor sozinho (auto-incremento) — nunca vai preencher o id manualmente
    barbearia_id: int = Field(foreign_key="barbearia.id") 
    barbeiro_id: int = Field(foreign_key="barbeiro.id") 
    cliente_id: int = Field(foreign_key="cliente.id") 
    servico_id: int = Field(foreign_key="servico.id") 
    data_hora: datetime 
    status: str = Field(default="agendado") #status guarda um texto simples ("agendado", "confirmado", "concluido", "cancelado", "nao_compareceu")
    valor: float #esse é um padrão comum em sistemas que lidam com dinheiro. Agendamento.valor funciona como uma "foto" do preço no momento em que o agendamento foi criado (ele copia o valor de Servico.preco naquele instante, mas depois vive independente). Isso é diferente de Servico.preco, que é o preço atual, usado só quando cria um novo agendamento.
    observacoes: Optional[str] = None 
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    