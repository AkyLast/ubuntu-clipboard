from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QMenu, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap

class BarraSuperior(QFrame):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.posicao_arraste = None
        
        self.setCursor(Qt.SizeAllCursor)
        self.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        titulo = QLabel("Área de Transferência")
        titulo.setStyleSheet("color: #9e9e9e; font-size: 11px; font-weight: bold;")
        titulo.setAttribute(Qt.WA_TransparentForMouseEvents) 
        
        btn_desligar = QPushButton("⏻")
        btn_desligar.setFixedSize(28, 28)
        btn_desligar.setCursor(Qt.PointingHandCursor)
        btn_desligar.setStyleSheet("QPushButton { background-color: transparent; color: #9e9e9e; border: none; font-weight: bold; border-radius: 14px; font-size: 14px; } QPushButton:hover { background-color: #d32f2f; color: white; }")
        btn_desligar.clicked.connect(QApplication.instance().quit)

        btn_limpar = QPushButton("🗑")
        btn_limpar.setFixedSize(28, 28)
        btn_limpar.setCursor(Qt.PointingHandCursor)
        btn_limpar.setStyleSheet("QPushButton { background-color: transparent; color: #9e9e9e; border: none; font-weight: bold; border-radius: 14px; font-size: 14px; } QPushButton:hover { background-color: #f57c00; color: white; }")
        btn_limpar.clicked.connect(self.parent_window.limpar_clipboard)

        btn_esconder = QPushButton("✕")
        btn_esconder.setFixedSize(28, 28)
        btn_esconder.setCursor(Qt.PointingHandCursor)
        btn_esconder.setStyleSheet("QPushButton { background-color: transparent; color: #9e9e9e; border: none; font-weight: bold; border-radius: 14px; font-size: 14px; } QPushButton:hover { background-color: #555555; color: white; }")
        btn_esconder.clicked.connect(self.parent_window.hide)

        layout.addWidget(titulo)
        layout.addStretch()
        layout.addWidget(btn_desligar)
        layout.addWidget(btn_limpar)
        layout.addWidget(btn_esconder)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.posicao_arraste = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.posicao_arraste:
            movimento = event.globalPos() - self.posicao_arraste
            self.parent_window.move(self.parent_window.pos() + movimento)
            self.posicao_arraste = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.posicao_arraste = None

class ItemClipboard(QFrame):
    def __init__(self, tipo, conteudo, parent_window, db_id=None, is_favorite=False):
        super().__init__()
        self.tipo = tipo
        self.conteudo_completo = conteudo 
        self.parent_window = parent_window 
        self.db_id = db_id
        self.is_favorite = is_favorite
        
        self.estilo_padrao = "QFrame { background-color: #383737; border-radius: 8px; border: none; } QFrame:hover { background-color: #454444; border: none; }"
        self.estilo_copiado = "QFrame { background-color: #2e7d32; border-radius: 8px; border: none; }"
        
        self.setStyleSheet(self.estilo_padrao)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.label = QLabel()
        self.label.setStyleSheet("color: #e0e0e0; border: none; background-color: transparent;")

        texto_fav_prefixo = "⭐ " if self.is_favorite else ""

        if tipo == "texto":
            texto_limpo = conteudo.replace('\n', ' ') 
            
            limite = 220 if len(texto_limpo) > 100 else 75
            texto_exibicao = (texto_limpo[:limite] + "...") if len(texto_limpo) > limite else texto_limpo

            self.label.setText(texto_fav_prefixo + texto_exibicao)
            self.label.setWordWrap(True)
            self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.label.setFont(QFont("Segoe UI", 10))
            
        elif tipo == "imagem":
            self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.label.setAlignment(Qt.AlignCenter)
            
            pixmap = conteudo if isinstance(conteudo, QPixmap) else QPixmap(conteudo)
            
            if pixmap.isNull():
                self.label.setText(texto_fav_prefixo + "[ Imagem não encontrada ]")
                self.label.setStyleSheet("color: #888;")
                self.label.setFixedSize(280, 80)
            else:
                pixmap_redimensionado = pixmap.scaled(280, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label.setPixmap(pixmap_redimensionado)
                
        layout.addWidget(self.label)

    def toggle_favorite(self):
        if self.is_favorite:
            if self.db_id:
                self.parent_window.remover_favorito(self.db_id)
            self.is_favorite = False
            self.db_id = None
            if self.tipo == "texto":
                self.label.setText(self.label.text().replace("⭐ ", "", 1))
        else:
            self.db_id = self.parent_window.salvar_favorito(self.tipo, self.conteudo_completo)
            self.is_favorite = True
            if self.tipo == "texto":
                self.label.setText("⭐ " + self.label.text())

    def copiar_conteudo(self):
        clipboard = QApplication.clipboard()
        
        if self.tipo == "texto":
            self.parent_window.ultimo_texto = self.conteudo_completo
            self.parent_window.ultima_imagem = None
            clipboard.setText(self.conteudo_completo)
        elif self.tipo == "imagem":
            pixmap = self.conteudo_completo if isinstance(self.conteudo_completo, QPixmap) else QPixmap(self.conteudo_completo)
            self.parent_window.ultima_imagem = pixmap.toImage()
            self.parent_window.ultimo_texto = None
            clipboard.setPixmap(pixmap)
        
        self.setStyleSheet(self.estilo_copiado)
        QTimer.singleShot(400, lambda: self.setStyleSheet(self.estilo_padrao))
        QTimer.singleShot(200, self.parent_window.hide)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.copiar_conteudo()
        elif event.button() == Qt.RightButton:
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu { background-color: #2b2a2a; color: white; border: 1px solid #555; padding: 4px; border-radius: 4px; }
                QMenu::item { padding: 6px 20px; border-radius: 4px; }
                QMenu::item:selected { background-color: #4a4a4a; }
            """)
            
            acao_copiar = menu.addAction("Copiar")
            texto_fav = "Desfavoritar" if self.is_favorite else "Favoritar"
            acao_fav = menu.addAction(texto_fav)
            
            acao = menu.exec_(event.globalPos())
            
            if acao == acao_copiar:
                self.copiar_conteudo()
            elif acao == acao_fav:
                self.toggle_favorite()
