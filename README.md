# integracaoSeniorGupy
123007 - Solicitação de Integração via API Cadastro de Colaboradores na Gupy

### Estrutura do projeto

```
├── data/                      # Dados de exportações do RH
│   ├── colaboradores_ativos.json
│   ├── usuarios_sistema.json
│   ├── connectionDB.py
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
│   ├── config.py
│   ├── logger.py
│   ├── database.py
│
├── logs/                      # Logs de execução e auditoria
│   ├── execucao.log
│
├── README.md                  # Documentação do projeto
```