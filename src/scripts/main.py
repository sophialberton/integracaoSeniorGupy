from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scripts.remover_ex_colaboradores import remover_ex_colaboradores
from scripts.atribuir_permissoes import atribuir_permissoes
from scripts.registrar_inscricao import registrar_inscricao
from utils.database import get_active_employees, get_system_users, update_users, log_action

app = FastAPI(title="Automação de Colaboradores")

# Modelos de entrada
class InscricaoRequest(BaseModel):
    employee_id: str
    program_name: str

class AdmissaoRequest(BaseModel):
    employee_id: str
    role: str
    name: str

class DesligamentoRequest(BaseModel):
    employee_id: str

# Endpoint para sincronizar usuários (remover ex-colaboradores e atualizar permissões)
@app.post("/sincronizar")
def sincronizar_usuarios():
    ativos = get_active_employees()
    sistema = get_system_users()

    atualizados, removidos = remover_ex_colaboradores(sistema, ativos)
    atualizados = atribuir_permissoes(atualizados)

    update_users(atualizados)
    log_action("Removidos", removidos)

    return {"atualizados": atualizados, "removidos": removidos}

# Endpoint para registrar inscrição interna
@app.post("/inscricao")
def nova_inscricao(request: InscricaoRequest):
    registro = registrar_inscricao(request.employee_id, request.program_name)
    log_action("Inscrição", registro)
    return {"mensagem": "Inscrição registrada com sucesso", "registro": registro}

# Endpoint para admissão
@app.post("/admissao")
def nova_admissao(request: AdmissaoRequest):
    # Aqui você adicionaria o colaborador ao banco e atualizaria permissões
    log_action("Admissão", request.dict())
    return {"mensagem": "Admissão registrada com sucesso"}

# Endpoint para desligamento
@app.post("/desligamento")
def novo_desligamento(request: DesligamentoRequest):
    # Aqui você removeria o colaborador do banco
    log_action("Desligamento", request.dict())
    return {"mensagem": "Desligamento registrado com sucesso"}
