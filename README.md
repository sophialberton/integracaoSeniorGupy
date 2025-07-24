# integracaoSeniorGupy
123007 - Solicitação de Integração via API Cadastro de Colaboradores na Gupy

### Estrutura do projeto

```
├── data/                      # Dados simulados ou reais (ex: exportações do RH)
│   ├── colaboradores_ativos.json
│   ├── usuarios_sistema.json
│
├── scripts/                   # Scripts Python principais
│   ├── remover_ex_colaboradores.py
│   ├── atribuir_permissoes.py
│   ├── registrar_inscricao.py
│   ├── main.py                # Script principal que orquestra tudo
│
├── utils/                     # Funções auxiliares
│   ├── carregar_dados.py
│   ├── salvar_dados.py
│
├── logs/                      # Logs de execução e auditoria
│   ├── execucao.log
│
├── README.md                  # Documentação do projeto
```