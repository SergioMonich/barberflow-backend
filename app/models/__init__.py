#o SQLModel só 'sabe' de uma tabela quando a classe é importada em algum lugar

from app.models.usuario import Usuario 
from app.models.barbearia import Barbearia 
from app.models.barbeiro import Barbeiro 
from app.models.cliente import Cliente 
from app.models.servico import Servico 
from app.models.categoria_financeira import CategoriaFinanceira 
from app.models.agendamento import Agendamento 
from app.models.financeiro import MovimentacaoFinanceira