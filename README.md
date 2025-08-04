# integracaoSeniorGupy
123007 - Solicitação de Integração via API Cadastro de Colaboradores na Gupy


### Pendencias
```
pip install python-dotenv requests oracledb
```

### Estrutura do projeto

```
├── data/                      # Dados de exportações do RH
│   ├── connectionDB.py
│
├── scripts/                   # Scripts Python principais
│   ├── main.py                # Script principal que orquestra tudo
|   ├── conexaoGupy.py         # Consome API da gupy
│
├── utils/                     # Funções auxiliares
│   ├── config.py
│
├── README.md                  # Documentação do projeto
```