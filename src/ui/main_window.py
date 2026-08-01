from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QStackedWidget, QScrollArea, QApplication
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont

from src.database import DatabaseManager
from src.ui.components import BarraSuperior, ItemClipboard

class JanelaClipboard(QWidget):
    def __init__(self):
        super().__init__()
        self.grupos = ["Recentes", "Frases", "Texto", "Imagens", "Favoritos"]
        self.botoes_abas = []
        self.layouts_grupos = {}
        
        self.ultimo_texto = None
        self.ultima_imagem = None
        
        self.db = DatabaseManager()
        
        self.init_ui()
        self.carregar_favoritos()
        self.iniciar_escuta_clipboard()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(450, 560)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        self.container = QFrame(self)
        self.container.setStyleSheet("QFrame#main_container { background-color: #2b2a2a; border-radius: 12px; border: 1px solid #424141; }")
        self.container.setObjectName("main_container")

        layout_container = QVBoxLayout(self.container)
        layout_container.setContentsMargins(15, 10, 15, 15)
        layout_container.setSpacing(10)

        self.barra_superior = BarraSuperior(self)
        layout_container.addWidget(self.barra_superior)

        barra_abas = QHBoxLayout()
        barra_abas.setSpacing(5)
        
        for i, nome in enumerate(self.grupos):
            btn = QPushButton(nome)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 9, QFont.Bold)) 
            btn.clicked.connect(lambda checked, index=i: self.mudar_aba(index))
            barra_abas.addWidget(btn)
            self.botoes_abas.append(btn)
            
        layout_container.addLayout(barra_abas)

        self.stacked_widget = QStackedWidget()
        layout_container.addWidget(self.stacked_widget)

        for nome in self.grupos:
            pagina = QWidget()
            layout_pagina = QVBoxLayout(pagina)
            layout_pagina.setContentsMargins(0, 5, 0, 0)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            scroll.setStyleSheet("""
                QScrollArea { border: none; background-color: transparent; }
                QScrollBar:vertical { background: transparent; width: 6px; margin: 0px; }
                QScrollBar::handle:vertical { background: #666; border-radius: 3px; min-height: 20px; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            """)

            scroll_widget = QWidget()
            scroll_widget.setStyleSheet("background-color: transparent;")
            
            layout_itens = QVBoxLayout(scroll_widget)
            layout_itens.setContentsMargins(0, 0, 8, 0)
            layout_itens.setSpacing(8)
            layout_itens.setAlignment(Qt.AlignTop)

            scroll.setWidget(scroll_widget)
            layout_pagina.addWidget(scroll)
            
            self.stacked_widget.addWidget(pagina)
            self.layouts_grupos[nome] = layout_itens

        layout_principal.addWidget(self.container)
        self.mudar_aba(0)

    def limpar_clipboard(self):
        for nome_layout, layout in self.layouts_grupos.items():
            if nome_layout == "Favoritos":
                continue 
            
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                    
        self.ultimo_texto = None
        self.ultima_imagem = None

    def changeEvent(self, event):
        if event.type() == QEvent.ActivationChange:
            if not self.isActiveWindow():
                self.hide()
        super().changeEvent(event)

    def mostrar_e_focar(self):
        self.posicionar_canto_inferior()
        self.show()
        self.activateWindow()
        self.raise_()

    def iniciar_escuta_clipboard(self):
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.ler_clipboard_seguro)

    def ler_clipboard_seguro(self):
        mime_data = self.clipboard.mimeData()

        if mime_data.hasImage():
            pixmap = self.clipboard.pixmap()
            if not pixmap.isNull():
                imagem_atual = pixmap.toImage()
                if self.ultima_imagem and self.ultima_imagem == imagem_atual: return
                self.ultima_imagem = imagem_atual
                self.ultimo_texto = None
                self.adicionar_item(pixmap, tipo="imagem")
                
        elif mime_data.hasText():
            texto = mime_data.text().strip()
            if not texto: return
            if self.ultimo_texto == texto: return
            self.ultimo_texto = texto
            self.ultima_imagem = None
            self.adicionar_item(texto, tipo="texto")

    def mudar_aba(self, index):
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.botoes_abas):
            if i == index:
                btn.setStyleSheet("QPushButton { background-color: #4a4a4a; color: #ffffff; border-radius: 6px; padding: 6px; border: none; }")
            else:
                btn.setStyleSheet("QPushButton { background-color: transparent; color: #888888; border-radius: 6px; padding: 6px; border: none; } QPushButton:hover { background-color: #383737; color: #ccc; }")

    def adicionar_item(self, conteudo, tipo="texto"):
        if tipo == "imagem": 
            grupo_alvo = "Imagens"
        else: 
            grupo_alvo = "Texto" if len(conteudo) > 100 else "Frases"

        layout_alvo = self.layouts_grupos[grupo_alvo]
        layout_alvo.insertWidget(0, ItemClipboard(tipo, conteudo, self))

        layout_recentes = self.layouts_grupos["Recentes"]
        layout_recentes.insertWidget(0, ItemClipboard(tipo, conteudo, self))
        
        for nome_layout, layout in self.layouts_grupos.items():
            if nome_layout == "Favoritos":
                continue
            limite = 15 if nome_layout == "Recentes" else 50
            while layout.count() > limite:
                indice_ultimo = layout.count() - 1
                item_para_remover = layout.takeAt(indice_ultimo)
                if item_para_remover.widget():
                    item_para_remover.widget().deleteLater()

    def salvar_favorito(self, tipo, conteudo):
        db_id = self.db.salvar_favorito(tipo, conteudo)
        item_fav = ItemClipboard(tipo, conteudo, self, db_id=db_id, is_favorite=True)
        self.layouts_grupos["Favoritos"].insertWidget(0, item_fav)
        return db_id

    def remover_favorito(self, db_id):
        self.db.remover_favorito(db_id)
        layout_fav = self.layouts_grupos["Favoritos"]
        for i in range(layout_fav.count()):
            widget = layout_fav.itemAt(i).widget()
            if widget and hasattr(widget, 'db_id') and getattr(widget, 'db_id') == db_id:
                layout_fav.takeAt(i)
                widget.deleteLater()
                break

    def carregar_favoritos(self):
        favoritos = self.db.carregar_favoritos()
        for db_id, tipo, conteudo in favoritos:
            item = ItemClipboard(tipo, conteudo, self, db_id=db_id, is_favorite=True)
            self.layouts_grupos["Favoritos"].addWidget(item)

    def posicionar_canto_inferior(self):
        tela = QApplication.primaryScreen().geometry()
        self.move(tela.width() - self.width() - 20, tela.height() - self.height() - 60)
