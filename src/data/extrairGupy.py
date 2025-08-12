import os
import csv
import requests

class ExtratorGupy:
    def __init__(self):
        self.token = os.getenv("token")

    def extracaoCargosGupy(self):
        if not self.token:
            print("Token nao encontrado. Defina a variável de ambiente 'token'.")
            return

        base_url = "https://api.gupy.io/api/v1/departments"
        per_page = 10
        total_pages = 60
        diretorioLocal = os.getcwd()
        csv_directory = f"{diretorioLocal}/src/data/extracaoGupy/" 
        csv_file_path = os.path.join(csv_directory, "areagupy.csv")

        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['id', 'name', 'code', 'similarTo', 'createdAt', 'updatedAt'])

            for page in range(1, total_pages + 1):
                print(f"Processando página {page}...")
                params = {'perPage': per_page, 'page': page}
                headers = {"Authorization": f"Bearer {self.token}"}

                try:
                    response = requests.get(base_url, params=params, headers=headers, timeout=10)
                    response.raise_for_status()
                    data = response.json()

                    for item in data.get('results', []):
                        writer.writerow([
                            item.get('id'),
                            item.get('name'),
                            item.get('code'),
                            item.get('similarTo'),
                            item.get('createdAt'),
                            item.get('updatedAt')
                        ])
                except requests.exceptions.RequestException as e:
                    print(f"Erro na página {page}: {e}")

# Para executar:
extrator = ExtratorGupy()
extrator.extracaoCargosGupy()
