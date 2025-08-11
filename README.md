# integracaoSeniorGupy
Chamado: 123007 - Solicitação de Integração via API Cadastro de Colaboradores na Gupy
>Olá, time!
>Gostaríamos de solicitar o apoio de vocês para viabilizar a integração via API entre os sistemas, com o objetivo de manter o cadastro de colaboradores na Gupy sempre atualizado.
>Essa automação é fundamental para garantir:
>A facilidade nas inscrições internas de colaboradores;
>A remoção automática de usuários que não fazem mais parte da empresa, reforçando o compromisso com a conformidade (compliance);
>A liberação dos acessos corretos no momento da admissão concluída, conforme o cargo de cada colaborador.
>Essa iniciativa já foi alinhada com o Adriano, e abaixo seguem os links de referência do suporte GUPY:
>Links:
>https://suporte.gupy.io/s/suporte/article/Como-utilizar-a-API-da-Gupy-Operacoes-disponiveis?language=pt_BR#h_01F24ZARWPEM2CB3QK4TJTC38G

## Checklist de Integração v.1 (11/08)
- [x] A remoção automática de usuários que não fazem mais parte da empresa, reforçando o compromisso com a conformidade (compliance)
- [ ] A liberação dos acessos corretos no momento da admissão concluída, conforme o cargo de cada colaborador.

### Visão geral do projeto
O projeto é um script de integração Python projetado para sincronizar dados de colaboradores de um banco de dados **Senior** com um sistema **Gupy**. O processo envolve a busca de informações de colaboradores no banco de dados Senior, a validação e classificação desses dados, e a posterior criação, atualização ou exclusão de usuários na API Gupy com base no status do colaborador.

### Tecnologias Utilizadas
O código utiliza as seguintes bibliotecas e tecnologias:
- **Python**: A linguagem de programação principal do projeto.
- **Pandas**: Usado para manipulação e análise de dados, formatando os resultados da consulta SQL em um `DataFrame` para facilitar o processamento.
- **Oracledb**: Biblioteca oficial da Oracle para conectar-se e interagir com o banco de dados Oracle, utilizado aqui para a conexão com o banco de dados Senior.
- **Requests**: Uma biblioteca HTTP para Python, usada para fazer chamadas à API da Gupy (listar, criar e deletar usuários).
- **python-dotenv**: Permite carregar variáveis de ambiente de um arquivo `.env` para gerenciar segredos como credenciais de banco de dados e tokens de API.
- **Logging**: O módulo de log do Python é usado para registrar informações, avisos e erros durante a execução do script.
- **Collections (defaultdict)**: Usado para agrupar os colaboradores por CPF.
- **CSV**: Usado para ler a lista de CPFs a serem ignorados de um arquivo CSV.
- **Datetime e Socket**: Usados no módulo `main.py` para gerar informações de log, incluindo o carimbo de data/hora e o nome do host/IP.

### Pendencias
- Estão todas dentro de requirements.txt: 
```
pip install -r requirements.txt
```

### Lógica e Fluxo do Código

1. **Inicialização (`main.py`)**: O script começa no arquivo `main.py`, onde a configuração de logs é definida. Em seguida, ele estabelece a conexão com o banco de dados Senior e busca a lista completa de colaboradores.

2. **Conexão e Extração de Dados (`conexaoSenior.py`)**: A classe `DatabaseSenior` se conecta ao banco de dados Oracle usando credenciais de um arquivo `.env`. Em seguida, a função `buscaColaboradorSenior` executa uma consulta SQL complexa para extrair dados de funcionários, incluindo `Empresa`, `Nome`, `TipoColaborador`, `Matricula`, `Cpf`, `Situacao` e `Email`. Os resultados são retornados como um `DataFrame` do Pandas.

3. **Processamento e Classificação (`ponteSeniorGupy.py` e `colaboradores.py`)**: Os dados brutos dos colaboradores são passados para a classe `ponteSeniorGupy` que, por sua vez, utiliza as funções de `colaboradores.py` para processar a informação.
    - É carregada uma lista de CPFs de um arquivo `ignoradosRH.csv`.
    - A função `classificar_usuarios_df` limpa e valida os e-mails, e classifica os colaboradores em três grupos: `validos` (com e-mail válido), `invalidos` (sem e-mail válido) e `ignorados` (CPFs listados no arquivo CSV).
    - Os usuários são agrupados por CPF para tratar casos de múltiplas matrículas.

4. **Sincronização com Gupy (`conexaoGupy.py`)**: A função `processar_cpf_df` (em `colaboradores.py`) itera sobre cada grupo de CPFs e determina a ação a ser tomada com base na situação do colaborador.
    - Se todas as matrículas de um CPF estiverem com a `Situação = 7` (indicando que foram desligadas), a função `deletaUsuarioGupy` é chamada para remover o usuário na Gupy.
    - Se pelo menos uma matrícula estiver ativa, o script verifica se o usuário já existe na Gupy usando a função `listaUsuariosGupy`. Essa função busca o usuário usando o e-mail principal e, se necessário, um e-mail alternativo.
    - Se o usuário não for encontrado na Gupy, mas tiver um e-mail válido, a função `criaUsuarioGupy` é chamada.

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
│   ├── config.py          # Habilita token da Gupy e dados da Senior 
|   ├── colaboradores.py   # Funções auxiliares
│
├── README.md                  # Documentação do projeto
```

### Breve Documentação Técnica
- `src/scripts/main.py`: O ponto de entrada da aplicação. Configura o logging e inicia o fluxo de sincronização chamando as funções de conexão e processamento.
- `src/scripts/ponteSeniorGupy.py`: Orquestra o fluxo principal de sincronização. Instancia as classes de conexão e chama as funções de processamento de dados.
- `src/data/conexaoSenior.py`: Define a classe `DatabaseSenior` para gerenciar a conexão com o banco de dados Oracle e executar a consulta SQL para extrair os dados dos colaboradores.
- `src/data/conexaoGupy.py`: Define a classe `conexaoGupy` para interagir com a API da Gupy. Contém métodos para listar, criar e deletar usuários, lidando com autenticação via token e diferentes domínios de e-mail.
- `src/utils/colaboradores.py`: Um módulo de utilitários que contém a lógica de processamento de dados. Inclui funções para carregar CPFs ignorados, classificar usuários, agrupar por CPF e a função central `processar_cpf_df` para determinar as ações na Gupy.
- `src/utils/config.py`: Arquivo de configuração que carrega variáveis de ambiente de um arquivo `.env`, tornando as credenciais e tokens seguros e reutilizáveis.
- `src/data/ignoradosRH.csv`: Arquivo CSV que contém a lista de CPFs que devem ser ignorados durante a sincronização, garantindo que certos colaboradores não sejam processados.