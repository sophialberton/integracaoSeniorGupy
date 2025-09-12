Incluir testes automatizados sem de fato utilizar a API e fazer alterações

dadosSenior ficará dentro de conexao Senior, entregando dados já tratados
processar colaboradores deve ser refatorado ao maximo e integrado na main

todos arquivos de utils e arquivos csv no geral devem ser organizados e refatorados, deixar apenas o essencial e de facil manutanção no futuro.

Atualizar docuementação no readme e estrutura geral, foco em clean code preservando a leitura logica refatorada e funcional para manutençoes futuras e facilitar documentação.

Apis -> Graph para envio do log no email 
     -> Gupy toda as funções principais
Banco de dados
     -> Oracle Senior para dados do RH/colaboradores da empresa.

Se tiver sugestão do que melhorar na extracao Gupy e similar to ou tratamento de dados que englobe os ignorados (acho que ja esta sendo tratado) 

se quiser reaproveitar o classificar usuarios de outro projeto pode usar, desde que mantenha a logica desse certa...

Nao altere select
Use pandas
Funções novas e antigas devem ter nome padronizados e descritivos em portugues

o encadeamento esta extremamente confuso... mas funciona... e deve continuar funcionando apos a refatoração

Se encontrar possiveis erros de lógica me avise
├── .gitignore
├── README.md
├── requirements.txt
├── env.example
├── main.py
├── config.py
│
├── dados/
│   ├── ignoradosRH.csv
│   └── extracao_gupy/
│       ├── areaGupy.csv
│       ├── cargosGupy.csv
│       └── filialGupy.csv
│
├── logs/
│   └── YYYY-MM-DD_log.log
│
├── servicos/
│   ├── conexao_senior.py
│   ├── conexao_gupy.py
│   └── servico_email.py
│
├── utils/
│   ├── colaboradores.py
│   ├── mapeamentos.py
│   └── helpers.py
│
└── testes/
    ├── test_colaboradores.py
    └── test_conexoes.py    

REGRAS A IMPLEMENTAR: 

- O UNICO EMAIL VÁLIDO QUE DEVE SER USADO DEVE SER DO ENDEREÇO fgmdentalgroup.com, ignore o @fgm.ind.br, se ele tiver apenas o @fgm.ind.br ou nenhum, coloque na lista de PRECISA_ATAULIZAR_EMAIL
- ANTES DE CRIAR QUALQUER COISA
     - ***DEVE*** VERIFICAR SE TAL USUARIO, CARGO, BRANCH, DEPARTAMENTO já existe
          - Usuario consulta pelo email, se JÀ tem um email @fgm.ind.br ou fgmdentalgroup.com cadastrado no nome dele -> NAO CRIA
          - Cargo e departamento deve ser buscados como "Semelhantes" ou "equivalentes"
          - Branch/Filial tambem.
- 


PS C:\github\integracaoSeniorGupy> python main.py
2025-09-12 12:57:07 INFO Executando em: HOST=DEN-NOTE-06000, IP=10.1.8.103
2025-09-12 12:57:07 INFO >>> Iniciando processo de integração Senior-Gupy.
2025-09-12 12:57:07 INFO Conexão com o banco de dados Senior estabelecida com sucesso.
C:\github\integracaoSeniorGupy\servicos\conexao_senior.py:87: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
  df = pd.read_sql_query(query, self.connection)
2025-09-12 12:57:08 INFO Consulta ao Senior retornou 720 registros.
2025-09-12 12:57:08 INFO Total de registros recebidos do Senior: 720
2025-09-12 12:57:08 INFO Registros com e-mail válido para processar: 574
2025-09-12 12:57:08 INFO Registros sem e-mail válido nos domínios: 138
2025-09-12 12:57:08 INFO Registros ignorados por CPF: 8
2025-09-12 12:57:08 INFO Processando CPF: 00254820174 - Nome: Douglas Agustini
2025-09-12 12:57:09 INFO Colaborador ativo não encontrado na Gupy. Criando usuário: Douglas Agustini
2025-09-12 12:57:11 INFO Usuário criado na Gupy: Douglas Agustini (douglas.agustini@fgm.ind.br)
2025-09-12 12:57:11 CRITICAL Ocorreu um erro inesperado no processo principal: 'ServicoGupy' object has no attribute 'obter_ou_criar_cargo'
Traceback (most recent call last):
  File "C:\github\integracaoSeniorGupy\main.py", line 50, in main
    processar_colaboradores(servico_gupy, colaboradores_df)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\github\integracaoSeniorGupy\utils\colaboradores.py", line 120, in processar_colaboradores
    dados_para_atualizar = _obter_ou_criar_dados_gupy(servico_gupy, registro_principal)
  File "C:\github\integracaoSeniorGupy\utils\colaboradores.py", line 54, in _obter_ou_criar_dados_gupy
    cargo_id = servico_gupy.obter_ou_criar_cargo(nome_cargo, similar_to_cargo)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'ServicoGupy' object has no attribute 'obter_ou_criar_cargo'
2025-09-12 12:57:11 INFO Conexão com o banco de dados Senior fechada.
2025-09-12 12:57:11 INFO >>> Processo finalizado.
2025-09-12 12:57:11 INFO Token de acesso para o MS Graph obtido com sucesso.
2025-09-12 12:57:13 ERROR Falha ao enviar e-mail de log: 503 - Authentication Concurrency Limit Reached
PS C:\github\integracaoSeniorGupy> 

esse foi o log...
