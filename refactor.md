dadosSenior ficará dentro de conexao Senior, entregando dados já tratados
processar colaboradores deve ser refatorado ao maximo e integrado na main

todos arquivos de utils e arquivos csv no geral devem ser organizados e refatorados, deixar apenas o essencial e de facil manutanção no futuro.

Atualizar docuementação no readme e estrutura geral, foco em clean code preservando a leitura logica refatorada e funcional para manutençoes futuras e facilitar documentação.

Apis -> Graph para envio do log no email 
    -> Gupy toda as funções principais
Banco de dados
    _> Oracle Senior para dados do RH/colaboradores da empresa.

Se tiver sugestão do que melhorar na extracao Gupy e similar to ou tratamento de dados que englobe os ignorados (acho que ja esta sendo tratado) 

se quiser reaproveitar o classificar usuarios de outro projeto pode usar, desde que mantenha a logica desse certa...

o encadeamento esta extremamente confuso... mas funciona... e deve continuar funcionando apos a refatoração

# Integração Senior-Gupy

## Visão Geral do Projeto

Este projeto consiste em um script de integração em Python desenvolvido para sincronizar os dados de colaboradores do sistema Senior com a plataforma Gupy. O processo automatiza a gestão de usuários na Gupy, garantindo que as informações estejam sempre atualizadas. As principais funcionalidades incluem:

-   **Criação de novos usuários:** Colaboradores admitidos no Senior são automaticamente cadastrados na Gupy.
-   **Atualização de dados:** Modificações nos dados dos colaboradores no Senior (como cargo, departamento, etc.) são refletidas na Gupy.
-   **Remoção de usuários:** Colaboradores desligados no Senior são automaticamente removidos da Gupy, garantindo a conformidade e a segurança dos dados.

## Tecnologias Utilizadas

-   **Python:** Linguagem de programação principal.
-   **Pandas:** Para manipulação e análise dos dados extraídos do Senior.
-   **Oracledb:** Para conexão e interação com o banco de dados Oracle do Senior.
-   **Requests:** Para realizar as chamadas à API da Gupy.
-   **python-dotenv:** Para gerenciamento de variáveis de ambiente e segredos.

## Estrutura do Projeto

integracaoSeniorGupy/
├── Logs/                     # Diretório para arquivos de log
├── src/
│   ├── data/
│   │   ├── conexaoGraph.py   # Conexão com a API do Microsoft Graph para envio de e-mails
│   │   ├── conexaoGupy.py    # Funções para interagir com a API da Gupy
│   │   ├── conexaoSenior.py  # Conexão e extração de dados do banco de dados Senior
│   │   └── ignoradosRH.csv   # Lista de CPFs a serem ignorados no processo
│   ├── script/
│   │   └── main.py           # Ponto de entrada da aplicação
│   └── utils/
│       ├── camposCadastros.py # Lógica para processar e mapear campos
│       ├── colaboradores.py   # Funções para classificar e processar os dados dos colaboradores
│       ├── comum.py           # Mapeamentos de dados
│       └── config.py          # Configuração de variáveis de ambiente
│       └── helpers.py         # Funções auxiliares
├── .gitignore
├── env.exemple
├── LICENSE
├── README.md
└── requirements.txt

integracaoSeniorGupy/
├── Logs/
├── config/
│   ├── __init__.py
│   └── mappings.py         # Mapeamentos de cargos e departamentos
├── connectors/
│   ├── __init__.py
│   ├── graph_connector.py  # Lógica de conexão com a API do Microsoft Graph
│   ├── gupy_connector.py   # Lógica de conexão com a API da Gupy
│   └── senior_connector.py # Lógica de conexão com o banco de dados Senior
├── services/
│   ├── __init__.py
│   └── collaborator_service.py # Lógica de negócio para processar colaboradores
├── .env
├── .gitignore
├── main.py                   # Ponto de entrada da aplicação
├── README.md
└── requirements.txt



## Fluxo do Código

1.  **Inicialização (`main.py`):** O script principal (`main.py`) inicia o processo, configura os logs e estabelece a conexão com o banco de dados Senior.
2.  **Extração de Dados (`conexaoSenior.py`):** Os dados dos colaboradores são extraídos do banco de dados do Senior através de uma consulta SQL e carregados em um DataFrame do Pandas.
3.  **Processamento e Classificação (`colaboradores.py`):** Os dados extraídos são processados e classificados em:
    * **Válidos:** Colaboradores com dados completos e válidos.
    * **Inválidos:** Colaboradores com dados incompletos ou inválidos (ex: sem e-mail).
    * **Ignorados:** Colaboradores cujos CPFs estão na lista de `ignoradosRH.csv`.
4.  **Sincronização com a Gupy (`conexaoGupy.py` e `main.py`):** O script itera sobre os colaboradores classificados e realiza as seguintes ações na Gupy:
    * **Criação:** Cria novos usuários para os colaboradores admitidos.
    * **Atualização:** Atualiza os dados dos colaboradores existentes.
    * **Deleção:** Remove os usuários de colaboradores desligados.
5.  **Envio de Log (`conexaoGraph.py`):** Ao final do processo, um e-mail com o log d