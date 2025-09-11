# testes/test_colaboradores.py

import unittest
from unittest.mock import patch, mock_open
import pandas as pd

# Remover as linhas de "sys.path.insert" se ainda existirem
# from utils.colaboradores import carregar_cpfs_ignorados, classificar_usuarios
from utils.colaboradores import carregar_cpfs_ignorados, classificar_usuarios
from utils.helpers import extrair_email_valido

class TestProcessamentoColaboradores(unittest.TestCase):

    def setUp(self):
        """Prepara os dados que serão usados em múltiplos testes."""
        self.dados_exemplo = {
            'Nome': ['Alice Ativa', 'Beto Invalido', 'Carla Ignorada', 'Daniel Desligado'],
            'Cpf': ['11111111111', '22222222222', '33333333333', '44444444444'],
            'Email': ['alice@fgmdentalgroup.com', 'beto@emailaleatorio.com', 'carla@fgm.ind.br', 'daniel@fgmdentalgroup.com'],
            'Situacao': [1, 1, 1, 7]
        }
        self.colaboradores_df = pd.DataFrame(self.dados_exemplo)
        self.cpfs_ignorados_set = {'33333333333'}

    def test_extrair_email_valido(self):
        """Testa se a função de extração de e-mail funciona corretamente."""
        self.assertEqual(extrair_email_valido("teste@fgmdentalgroup.com"), "teste@fgmdentalgroup.com")
        self.assertEqual(extrair_email_valido("teste@fgm.ind.br"), "teste@fgm.ind.br")
        self.assertIsNone(extrair_email_valido("teste@dominio-externo.com"))
        self.assertEqual(extrair_email_valido("email1@externo.com, email2@fgm.ind.br"), "email2@fgm.ind.br")
        self.assertIsNone(extrair_email_valido(None))

    def test_carregar_cpfs_ignorados(self):
        """Testa o carregamento de CPFs de um arquivo CSV simulado (mock)."""
        conteudo_csv_simulado = "NOME QUALQUER;33333333333\nOUTRO NOME;55555555555"
        with patch("builtins.open", mock_open(read_data=conteudo_csv_simulado)):
            cpfs = carregar_cpfs_ignorados("caminho/falso/para/ignorados.csv")
            self.assertIn("33333333333", cpfs)
            self.assertIn("55555555555", cpfs)
            self.assertEqual(len(cpfs), 2)

    def test_classificar_usuarios(self):
        """Testa a função principal de classificação."""
        df_validos, df_invalidos, df_ignorados = classificar_usuarios(
            self.colaboradores_df,
            self.cpfs_ignorados_set
        )
        self.assertEqual(len(df_validos), 2)  # Alice, Daniel
        self.assertEqual(len(df_invalidos), 1)  # Beto
        self.assertEqual(len(df_ignorados), 1)  # Carla
        self.assertIn('Alice Ativa', df_validos['Nome'].values)
        self.assertNotIn('Carla Ignorada', df_validos['Nome'].values)

if __name__ == '__main__':
    unittest.main()