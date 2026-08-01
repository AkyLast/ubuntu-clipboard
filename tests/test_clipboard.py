import sys
import os
import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QImage

# Ajuste de path para importar src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ui.components import ItemClipboard
from src.ui.main_window import JanelaClipboard

@pytest.fixture(scope="session")
def app():
    """Fixture que garante que existe uma QApplication viva pros testes do Qt."""
    app_instance = QApplication.instance()
    if not app_instance:
        app_instance = QApplication(sys.argv)
    yield app_instance

def test_truncamento_de_texto_longo(app):
    """Garante que textos muito longos são truncados para não quebrar o layout."""
    texto_longo = "A" * 300
    # Mock simples da main_window
    class DummyWindow:
        pass
    
    item = ItemClipboard(tipo="texto", conteudo=texto_longo, parent_window=DummyWindow())
    
    # O texto visível deve ser menor que o texto completo e conter '...'
    assert len(item.label.text()) <= 230
    assert item.label.text().endswith("...")
    assert item.conteudo_completo == texto_longo

def test_criacao_item_imagem(app):
    """Garante que a classe lida corretamente com QPixmap vazios (graceful degradation)."""
    class DummyWindow:
        pass
        
    pixmap_vazio = QPixmap()
    item = ItemClipboard(tipo="imagem", conteudo=pixmap_vazio, parent_window=DummyWindow())
    
    assert "Imagem não encontrada" in item.label.text()
