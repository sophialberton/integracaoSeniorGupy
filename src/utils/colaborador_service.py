import logging
import pandas as pd
import csv
from .helpers import format_text, find_similar_to, extract_valid_email
from config.mappings import ROLE_MAPPING, DEPARTMENT_MAPPING

class CollaboratorService:
    """Classe de serviço para processar dados de colaboradores."""
    
    def __init__(self, gupy_connector, ignored_cpfs_path):
        self.gupy_connector = gupy_connector
        self.ignored_cpfs = self._load_ignored_cpfs(ignored_cpfs_path)

    def _load_ignored_cpfs(self, file_path):
        """Carrega os CPFs a serem ignorados de um arquivo CSV."""
        logging.info(f"Carregando CPFs ignorados de: {file_path}")
        cpfs = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                for row in reader:
                    if len(row) >= 2:
                        cpf = row[1].strip()
                        if cpf:
                            cpfs.add(cpf)
        except FileNotFoundError:
            logging.error(f"Arquivo de CPFs ignorados não encontrado em: {file_path}")
        return cpfs

    def _classify_users(self, df):
        """Classifica os usuários em válidos, inválidos e ignorados."""
        df['Cpf'] = df['Cpf'].astype(str).str.strip().str.zfill(11)
        ignored_df = df[df['Cpf'].isin(self.ignored_cpfs)]
        remaining_df = df[~df['Cpf'].isin(self.ignored_cpfs)].copy()
        
        remaining_df['EmailValido'] = remaining_df['Email'].apply(extract_valid_email)
        valid_df = remaining_df[remaining_df['EmailValido'].notnull()].copy()
        invalid_df = remaining_df[remaining_df['EmailValido'].isnull()].copy()
        
        valid_df.drop(columns=['EmailValido'], inplace=True)
        invalid_df.drop(columns=['EmailValido'], inplace=True)
        
        return valid_df, invalid_df, ignored_df

    def process_collaborators(self, collaborators_df):
        """Processa a lista de colaboradores, sincronizando com a Gupy."""
        
        for col in ['Branch_gupy', 'Role_gupy', 'Departamento_gupy']:
            collaborators_df[col] = collaborators_df[col].apply(format_text)
            
        valid_df, invalid_df, ignored_df = self._classify_users(collaborators_df)
        
        logging.info(f"Total de registros válidos: {len(valid_df)}")
        logging.info(f"Total de registros inválidos: {len(invalid_df)}")
        logging.info(f"Total de registros ignorados: {len(ignored_df)}")

        grouped_by_cpf = valid_df.groupby('Cpf')
        for cpf, group_df in grouped_by_cpf:
            self._process_cpf_group(cpf, group_df)

    def _process_cpf_group(self, cpf, group_df):
        """Processa um grupo de registros para um CPF específico."""
        logging.info(f"Processando CPF: {cpf}")
        
        primary_record = group_df.iloc[0]
        email = extract_valid_email(primary_record['Email'])
        
        if not email:
            logging.warning(f"CPF {cpf} sem e-mail válido. Nenhuma ação será tomada.")
            return

        gupy_user = self.gupy_connector.get_user_by_email(email)

        is_dismissed = (group_df['Situacao'] == 7).all()

        if is_dismissed:
            if gupy_user:
                user_id = gupy_user['results'][0]['id']
                self.gupy_connector.delete_user(user_id)
                logging.info(f"Usuário com CPF {cpf} deletado da Gupy.")
        else:
            if not gupy_user:
                self.gupy_connector.create_user(primary_record['Nome'], email, cpf)
                logging.info(f"Usuário com CPF {cpf} criado na Gupy.")
            else:
                user_id = gupy_user['results'][0]['id']
                # Lógica para atualização de dados (cargo, departamento, etc.)
                self._update_gupy_user_data(user_id, primary_record)

    def _update_gupy_user_data(self, user_id, record):
        """Atualiza os dados de um usuário na Gupy."""
        
        # Mapeia os campos do Senior para os IDs da Gupy
        role_id = find_similar_to(record['Role_gupy'], ROLE_MAPPING)
        department_id = find_similar_to(record['Departamento_gupy'], DEPARTMENT_MAPPING)
        # ... (lógica para buscar ou criar branch e obter o ID)
        branch_id = "..." 

        update_payload = {
            "roleId": role_id,
            "departmentId": department_id,
            "branchIds": [branch_id],
        }
        
        # Remove chaves com valores nulos
        update_payload = {k: v for k, v in update_payload.items() if v is not None}

        if update_payload:
            self.gupy_connector.update_user(user_id, update_payload)
            logging.info(f"Dados do usuário com ID {user_id} atualizados na Gupy.")