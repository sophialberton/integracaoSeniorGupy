# integracaoSeniorGupy
123007 - Solicitação de Integração via API Cadastro de Colaboradores na Gupy


### Pendencias
```
pip install python-dotenv requests oracledb
```

### Estrutura do projeto

```
├── data/                      # Dados de exportações do Senior, API
│   ├── conexaoSenor.py     # Consulta com o banco de dados do Senior
|   ├── conexaoGupy.py      # Serviços da API da Gupy
|   ├── ignoradosRH.csv     # Lista de ignorados manual para garantia durante processo 
│
├── scripts/                   # Scripts Python principais
│   ├── main.py                # Script principal que orquestra tudo
|   ├── conexaoGupy.py         # Consome API da gupy e chama funções auxiliares
│
├── utils/                     # Funções auxiliares
│   ├── config.py          # Habilita token  da Gupy e dados da Senior 
|   ├── colaboradores.py   # Funções auxiliares
│
├── README.md                  # Documentação do projeto
```