# scripts/extrair_dados_gupy.py

import os
import csv
import requests
import logging
from dotenv import load_dotenv

class ExtratorGupy:
    """
    Classe para extrair dados (cargos, departamentos, filiais) da API da Gupy
    e salvá-los em arquivos CSV.
    """
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("TOKEN")
        self.base_url = "https://api.gupy.io/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
        self.diretorio_csv = os.path.join(os.getcwd(), "dados", "extracao_gupy")
        os.makedirs(self.diretorio_csv, exist_ok=True)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def _realizar_extracao(self, endpoint, nome_arquivo_csv, colunas):
        """Função genérica para extrair dados paginados de um endpoint da Gupy."""
        if not self.token:
            logging.error("Token da API Gupy não encontrado. Verifique o arquivo .env.")
            return

        caminho_arquivo = os.path.join(self.diretorio_csv, nome_arquivo_csv)
        logging.info(f"Iniciando extração para o endpoint '{endpoint}'. Salvando em '{caminho_arquivo}'...")

        try:
            with open(caminho_arquivo, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(colunas)
                
                pagina = 1
                while True:
                    params = {'perPage': 100, 'page': pagina}
                    response = requests.get(f"{self.base_url}/{endpoint}", headers=self.headers, params=params, timeout=20)
                    response.raise_for_status()
                    data = response.json()
                    
                    resultados = data.get('results', [])
                    if not resultados:
                        logging.info("Não há mais resultados para extrair.")
                        break
                    
                    for item in resultados:
                        writer.writerow([item.get(col) for col in colunas])
                    
                    logging.info(f"Página {pagina} processada com sucesso, {len(resultados)} itens extraídos.")
                    pagina += 1

        except requests.exceptions.HTTPError as e:
            logging.error(f"Erro HTTP durante a extração: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro de conexão durante a extração: {e}")
        except IOError as e:
            logging.error(f"Erro de escrita no arquivo CSV: {e}")

    def extrair_cargos(self):
        """Extrai todos os cargos (roles)."""
        self._realizar_extracao("roles", "cargosGupy.csv", ['id', 'name', 'code', 'similarTo', 'createdAt', 'updatedAt'])

    def extrair_departamentos(self):
        """Extrai todos os departamentos (departments)."""
        self._realizar_extracao("departments", "areaGupy.csv", ['id', 'name', 'code', 'similarTo', 'createdAt', 'updatedAt'])

    def extrair_filiais(self):
        """Extrai todas as filiais (branches)."""
        self._realizar_extracao("branches", "filialGupy.csv", ['id', 'name', 'code', 'path', 'createdAt', 'updatedAt'])


if __name__ == '__main__':
    extrator = ExtratorGupy()
    
    print("Iniciando extração de dados da Gupy...")
    
    print("\nExtraindo Cargos...")
    extrator.extrair_cargos()
    
    print("\nExtraindo Departamentos...")
    extrator.extrair_departamentos()
    
    print("\nExtraindo Filiais...")
    extrator.extrair_filiais()
    
    print("\nExtração concluída.")