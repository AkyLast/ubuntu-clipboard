import sys
import os

from PyQt5.QtWidgets import QApplication
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from PyQt5.QtGui import QIcon

from src.ui.main_window import JanelaClipboard

def setup_environment():
    # Força o modo de compatibilidade X11 para leitura global no Wayland/Ubuntu
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    # Suprime o aviso do Qt de incompatibilidade de display
    os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

def rodar_aplicacao():
    setup_environment()
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon.fromTheme("edit-paste"))
    
    SERVER_NAME = "daemon_clipboard_ubuntu"
    
    socket = QLocalSocket()
    socket.connectToServer(SERVER_NAME)
    if socket.waitForConnected(500):
        socket.write(b"MOSTRAR")
        socket.flush()
        socket.waitForBytesWritten(500)
        socket.disconnectFromServer()
        sys.exit(0)

    server = QLocalServer()
    server.removeServer(SERVER_NAME)
    server.listen(SERVER_NAME)

    janela = JanelaClipboard()

    def tratar_nova_chamada():
        client = server.nextPendingConnection()
        if client.waitForReadyRead(500):
            msg = client.readAll().data()
            if msg == b"MOSTRAR":
                janela.mostrar_e_focar() 
        client.disconnectFromServer()

    server.newConnection.connect(tratar_nova_chamada)
    app.setQuitOnLastWindowClosed(False)
    sys.exit(app.exec_())

if __name__ == '__main__':
    rodar_aplicacao()
