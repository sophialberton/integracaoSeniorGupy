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

Estrutura nova:
integracaoSeniorGupy/
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

Execute o Script em um Ambiente Controlado: Rode o script normalmente. Não se preocupe com ele "estragar" algo em massa, pois as criações serão pontuais.

Monitore os Logs Atentamente: Fique de olho nas mensagens de WARNING que indicam a criação de novos cargos, departamentos ou filiais. Anote todos que forem criados.

Valide na Gupy: Após a execução, entre na plataforma da Gupy e verifique os novos campos que foram criados. Compare com os que já existiam. Você provavelmente encontrará casos como o do "Líder de Produção" que mencionei.

Ajuste Fino do Mapeamento: Com base na sua validação, você terá uma lista de nomes do Senior que deveriam ser associados a cargos/departamentos já existentes na Gupy. Agora, você vai tratar isso com foco no único lugar necessário: o arquivo utils/mapeamento.py.

Por exemplo, se você descobrir que vários cargos do Senior como "Coord De Vendas", "Coordenador Comercial" deveriam ser o mesmo cargo "Coordenador de Vendas" na Gupy, você pode adicionar mais palavras-chave ao seu mapa para capturar essas variações.