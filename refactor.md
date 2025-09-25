Atualizar docuementação no readme e estrutura geral, foco em clean code preservando a leitura logica refatorada e funcional para manutençoes futuras e facilitar documentação.

Funções novas e antigas devem ter nome padronizados e descritivos em portugues

REGRAS A IMPLEMENTAR: 

Preciso implementar a função atualizar_uauario corretamente

Antes de atualizar deve verificar quais campos estão vazios do id

Todas as informaçõe deve ser buscadas pela função cria_e_obtem_dados_gupy

O email a ser considerado deve ser o que o lista_por email retornou, nao do banco de dados

talvez seja melhor faazer a validação de email dentro de processar_colaboradores pois assim que descobrir qual email do cpf esta sendo utilizado para o cadastro da gupy ai consegue atualizar corretamente

e se nao tiver nenhum emaikl sendo utilizado provavelmente o cpf nao tem cadastro na gupy e ai pode criar com o @fgmdental.group apenas, nao se cria mais com o fgm.ind.br, mas se estiver sendo utilizado mantem. 

O programa deve atualizar todos aquqles que tem campos vazios conforme o seu registro no banco de dados.

