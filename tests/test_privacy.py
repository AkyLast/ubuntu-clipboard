import sys
import os
import pytest
from PyQt5.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ui.main_window import JanelaClipboard
from src.database import DatabaseManager
from unittest.mock import patch
import tempfile

@pytest.fixture(scope="session")
def app():
    """Garante que existe uma QApplication viva pros testes do Qt."""
    app_instance = QApplication.instance()
    if not app_instance:
        app_instance = QApplication(sys.argv)
    yield app_instance

@patch('src.ui.main_window.DatabaseManager')
def test_privacidade_dados_volateis(mock_db_class, app):
    """
    Testa que um dado recém copiado entra apenas na memória RAM (Layout)
    e NÃO é salvo no banco de dados SQLite a menos que favoritado.
    """
    fd, temp_db_path = tempfile.mkstemp()
    os.close(fd)
    mock_db = DatabaseManager(temp_db_path)
    mock_db_class.return_value = mock_db
    
    janela = JanelaClipboard()
    
    texto_sensivel = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC3... user@machine" * 3
    
    janela.adicionar_item(texto_sensivel, tipo="texto")
    
    item_recente = janela.layouts_grupos["Recentes"].itemAt(0).widget()
    assert item_recente.conteudo_completo == texto_sensivel
    
    item_texto = janela.layouts_grupos["Texto"].itemAt(0).widget()
    assert item_texto.conteudo_completo == texto_sensivel
    
    favoritos_no_banco = janela.db.carregar_favoritos()
    encontrado_no_banco = any(fav['conteudo'] == texto_sensivel for fav in favoritos_no_banco)
    
    assert not encontrado_no_banco, "FALHA DE PRIVACIDADE: O dado sensível foi para o SQLite sem ser favoritado!"
    
@patch('src.ui.main_window.DatabaseManager')
def test_limpeza_de_historico_apaga_memoria(mock_db_class, app):
    """
    Testa que ao usar o botão de Limpeza, todos os dados sensíveis
    são imediatamente destruídos da memória RAM (layouts).
    """
    fd, temp_db_path = tempfile.mkstemp()
    os.close(fd)
    mock_db = DatabaseManager(temp_db_path)
    mock_db_class.return_value = mock_db

    janela = JanelaClipboard()
    texto_sensivel = "senha_banco_1234_muito_longa_para_cair_na_aba_texto_1234567890" * 3
    janela.adicionar_item(texto_sensivel, tipo="texto")
    
    assert janela.layouts_grupos["Recentes"].count() > 0
    assert janela.layouts_grupos["Texto"].count() > 0
    
    janela.limpar_clipboard()
    
    assert janela.layouts_grupos["Recentes"].count() == 0, "A memória de recentes não foi limpa!"
    assert janela.layouts_grupos["Texto"].count() == 0, "A memória de textos não foi limpa!"
