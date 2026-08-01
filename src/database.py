import sqlite3
from pathlib import Path
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QPixmap, QImage

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            data_dir = Path.home() / ".local" / "share" / "ubuntu-clipboard"
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = data_dir / "favorites.db"
        else:
            self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS favoritos
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      tipo TEXT,
                      conteudo BLOB)''')
        conn.commit()
        conn.close()

    def salvar_favorito(self, tipo, conteudo):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if tipo == "texto":
            bin_data = conteudo.encode('utf-8')
        else:
            img = conteudo.toImage() if isinstance(conteudo, QPixmap) else conteudo
            ba = QByteArray()
            buffer = QBuffer(ba)
            buffer.open(QIODevice.WriteOnly)
            img.save(buffer, "PNG")
            bin_data = ba.data()
            
        c.execute("INSERT INTO favoritos (tipo, conteudo) VALUES (?, ?)", (tipo, bin_data))
        conn.commit()
        db_id = c.lastrowid
        conn.close()
        
        return db_id

    def remover_favorito(self, db_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM favoritos WHERE id = ?", (db_id,))
        conn.commit()
        conn.close()

    def carregar_favoritos(self):
        favoritos = []
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, tipo, conteudo FROM favoritos ORDER BY id DESC")
        for row in c.fetchall():
            db_id, tipo, conteudo = row
            if tipo == "texto":
                conteudo_str = conteudo.decode('utf-8')
                favoritos.append((db_id, tipo, conteudo_str))
            else:
                img = QImage.fromData(conteudo)
                pixmap = QPixmap.fromImage(img)
                favoritos.append((db_id, tipo, pixmap))
        conn.close()
        return favoritos
