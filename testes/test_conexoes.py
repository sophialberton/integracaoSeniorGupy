# testes/test_conexoes.py

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from servicos.conexao_gupy import ServicoGupy
from servicos.conexao_senior import ServicoSenior

class TestServicosExternos(unittest.TestCase):

    @patch('servicos.conexao_senior.oracledb.connect')
    def test_conexao_senior_sucesso(self, mock_connect):
        """Testa a simulação de conexão com o Senior."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        servico_senior = ServicoSenior("user", "pass", "host", "port", "service")
        resultado = servico_senior.conectar()
        
        self.assertTrue(resultado)
        mock_connect.assert_called_once()
        servico_senior.desconectar()
        mock_connection.close.assert_called_once()

    @patch('servicos.conexao_gupy.requests.request')
    def test_gupy_listar_usuario_encontrado(self, mock_request):
        """Testa a simulação de listagem de usuário na Gupy."""
        resposta_simulada = {"results": [{"id": 123, "name": "Alice", "email": "alice@exemplo.com"}]}
        mock_response = MagicMock()
        mock_response.json.return_value = resposta_simulada
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        servico_gupy = ServicoGupy(token="fake_token")
        usuario = servico_gupy.listar_usuario_por_email("alice@exemplo.com")
        
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario['id'], 123)
        mock_request.assert_called_with(
            "get",
            "https://api.gupy.io/api/v1/users?email=alice@exemplo.com",
            headers={'Accept': 'application/json', 'Authorization': 'Bearer fake_token'},
            timeout=20
        )

    @patch('servicos.conexao_gupy.requests.request')
    def test_gupy_criar_usuario(self, mock_request):
        """Testa a simulação de criação de usuário na Gupy."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 456, "name": "Beto", "email": "beto@exemplo.com"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        servico_gupy = ServicoGupy(token="fake_token")
        servico_gupy.criar_usuario("Beto", "beto@exemplo.com", "12345678900")
        
        mock_request.assert_called_with(
            "post",
            "https://api.gupy.io/api/v1/users",
            headers={'Accept': 'application/json', 'Authorization': 'Bearer fake_token'},
            timeout=20,
            json={"name": "Beto", "email": "beto@exemplo.com"}
        )

if __name__ == '__main__':
    unittest.main()