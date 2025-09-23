Atualizar docuementação no readme e estrutura geral, foco em clean code preservando a leitura logica refatorada e funcional para manutençoes futuras e facilitar documentação.

Funções novas e antigas devem ter nome padronizados e descritivos em portugues

REGRAS A IMPLEMENTAR: 

Listar todos Cargo, departamento e filial que retornarem similarTo "none" para que eu possar encontrar um equivalente 

arrumar o criar/lista cargo e cria/lista filial seguindo a logica das outras funções.

Queria ajeitar o loggin geral para que focasse em cada usuario, fiando tipo:


     Processando CPF: 00254820174 - Nome: Douglas Agustini
          Nenhum id cadastrado encontrado para douglas.agustini@fgm.ind.br
          Encontrou id cadastro para douglas.agustini@fgmdentalgroup.com e id 671870
     Usuario com cadastro existente! Verificando necessidade de atualização.
          Campos já cadastrados:
               Cargo: COORDENADOR (A) QUALIDADE FORNECEDORES;
               Área: Pesquisa & Desenvolvimento;
               Filial: none;
          Campos novos:
               Cargo: ESPECIALISTA QUALIDADE DE PRODUTO - ESPECIALISTA
               Área: Engenharia Industrial - Engenharia Industrial
               Filial: 219 - Matriz

     Verificando se campos novos existem ou deve ser criado.
          - Cargo COORDENADOR (A) QUALIDADE FORNECEDORES Criado com similarTo: . 
          //  ou
          Cargo Coordenador Qualidade - Fornecedores existente com id 01202. 
          mesmo padrao para area e filial.

ou 
     Processando CPF: 00254820174 - Nome: Douglas Agustini
          Nenhum id cadastrado encontrado para douglas.agustini@fgm.ind.br
     Usuario sem cadastro existente! Criando e atualizando cadastro.
     ampos novos:
               Cargo: ESPECIALISTA QUALIDADE DE PRODUTO - ESPECIALISTA
               Área: Engenharia Industrial - Engenharia Industrial
               Filial: 219 - Matriz

     Verificando se campos novos existem ou deve ser criado.
          - Cargo COORDENADOR (A) QUALIDADE FORNECEDORES Criado com similarTo: . 
          //  ou
          Cargo Coordenador Qualidade - Fornecedores existente com id 01202. 
          mesmo padrao para area e filial.

Tipo isso...para melhor visualização

