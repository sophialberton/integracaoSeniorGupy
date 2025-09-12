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
E na refatoração na função def _realizar_requisicao(self, method, endpoint, **kwargs):
        """Função auxiliar para realizar requisições HTTP."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, timeout=20, **kwargs)
            response.raise_for_status()
            # Retorna None para status 204 (No Content) que é comum em DELETE
            if response.status_code == 204:
                return None
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"Erro HTTP na API Gupy para {url}: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro de conexão com a API Gupy para {url}: {e}")
        return None

algumas outras funções precisam de uma url diferente...

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


PS C:\github\integracaoSeniorGupy> python main.py
2025-09-12 14:07:14 INFO Executando em: HOST=DEN-NOTE-06000, IP=10.1.8.103
2025-09-12 14:07:14 INFO >>> Iniciando processo de integração Senior-Gupy.
2025-09-12 14:07:14 INFO Conexão com o banco de dados Senior estabelecida com sucesso.
C:\github\integracaoSeniorGupy\servicos\conexao_senior.py:87: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
  df = pd.read_sql_query(query, self.connection)
2025-09-12 14:07:14 INFO Consulta ao Senior retornou 720 registros.
2025-09-12 14:07:14 INFO Total de registros recebidos do Senior: 720
2025-09-12 14:07:14 INFO Registros com e-mail válido para processar: 574
2025-09-12 14:07:14 INFO Registros sem e-mail válido nos domínios: 138
2025-09-12 14:07:14 INFO Registros ignorados por CPF: 8
2025-09-12 14:07:14 INFO Processando CPF: 00254820174 - Nome: Douglas Agustini
2025-09-12 14:07:15 INFO Colaborador ativo não encontrado na Gupy. Criando usuário: Douglas Agustini
2025-09-12 14:07:16 INFO Usuário criado na Gupy: Douglas Agustini (douglas.agustini@fgm.ind.br)
2025-09-12 14:07:16 CRITICAL Ocorreu um erro inesperado no processo principal: 'ServicoGupy' object has no attribute 'obter_ou_criar_departamento'
Traceback (most recent call last):
  File "C:\github\integracaoSeniorGupy\main.py", line 50, in main
    processar_colaboradores(servico_gupy, colaboradores_df)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\github\integracaoSeniorGupy\utils\colaboradores.py", line 120, in processar_colaboradores
    dados_para_atualizar = _obter_ou_criar_dados_gupy(servico_gupy, registro_principal)
  File "C:\github\integracaoSeniorGupy\utils\colaboradores.py", line 63, in _obter_ou_criar_dados_gupy
    dep_id = servico_gupy.obter_ou_criar_departamento(nome_departamento, similar_to_dep)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'ServicoGupy' object has no attribute 'obter_ou_criar_departamento'
2025-09-12 14:07:16 INFO Conexão com o banco de dados Senior fechada.
2025-09-12 14:07:16 INFO >>> Processo finalizado.
2025-09-12 14:07:17 INFO Token de acesso para o MS Graph obtido com sucesso.
2025-09-12 14:07:18 INFO E-mail de log enviado com sucesso para sophia.alberton@fgmdentalgroup.com.
PS C:\github\integracaoSeniorGupy>


ele nao deveria criar o cadastro do douglas, posi ele ja tem! 


PS C:\github\integracaoSeniorGupy> python main.py
2025-09-12 14:36:29 INFO Executando em: HOST=DEN-NOTE-06000, IP=10.1.8.103
2025-09-12 14:36:29 INFO >>> Iniciando processo de integração Senior-Gupy.
2025-09-12 14:36:29 INFO Conexão com o banco de dados Senior estabelecida com sucesso.
C:\github\integracaoSeniorGupy\servicos\conexao_senior.py:87: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
  df = pd.read_sql_query(query, self.connection)
2025-09-12 14:36:29 INFO Consulta ao Senior retornou 720 registros.
2025-09-12 14:36:29 INFO Total de registros recebidos do Senior: 720
2025-09-12 14:36:29 INFO Registros com e-mail válido para processar: 574
2025-09-12 14:36:29 INFO Registros sem e-mail válido nos domínios: 138
2025-09-12 14:36:29 INFO Registros ignorados por CPF: 8
2025-09-12 14:36:29 INFO Processando CPF: 00254820174 - Nome: Douglas Agustini
> Nenhum id cadastrado encontrado para douglas.agustini@fgm.ind.br
2025-09-12 14:36:30 WARNING > Nenhum id cadastrado encontrado para douglas.agustini@fgm.ind.br
2025-09-12 14:36:31 INFO Colaborador ativo (Douglas Agustini) já existe na Gupy. Verificando necessidade de atualização.
2025-09-12 14:36:31 CRITICAL Ocorreu um erro inesperado no processo principal: 'ServicoGupy' object has no attribute 'obter_ou_criar_departamento'
Traceback (most recent call last):
  File "C:\github\integracaoSeniorGupy\main.py", line 50, in main
    processar_colaboradores(servico_gupy, colaboradores_df)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\github\integracaoSeniorGupy\utils\colaboradores.py", line 127, in processar_colaboradores
    dados_para_atualizar = _obter_ou_criar_dados_gupy(servico_gupy, registro_principal)
  File "C:\github\integracaoSeniorGupy\utils\colaboradores.py", line 63, in _obter_ou_criar_dados_gupy
    dep_id = servico_gupy.obter_ou_criar_departamento(nome_departamento, similar_to_dep)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'ServicoGupy' object has no attribute 'obter_ou_criar_departamento'
2025-09-12 14:36:31 INFO Conexão com o banco de dados Senior fechada.
2025-09-12 14:36:31 INFO >>> Processo finalizado.
2025-09-12 14:36:31 INFO Token de acesso para o MS Graph obtido com sucesso.
2025-09-12 14:36:32 INFO E-mail de log enviado com sucesso para sophia.alberton@fgmdentalgroup.com.