#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon

def setup_autostart():
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon.fromTheme("edit-paste"))
    
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_file = autostart_dir / "ubuntu-clipboard.desktop"
    
    if desktop_file.exists():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Configuração")
        msg.setText("O aplicativo já está configurado para iniciar junto com o sistema.")
        msg.exec_()
        return

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle("Configuração de Inicialização")
    msg.setText("Deseja iniciar o Histórico automaticamente com o Ubuntu?")
    msg.setInformativeText("Isso garante que o aplicativo comece a escutar a área de transferência silenciosamente no boot.\n\nSe você não ativar isso, precisará acionar o atalho duas vezes ao ligar o PC: a primeira rodará o processo em background e a segunda abrirá a interface.")
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.button(QMessageBox.Yes).setText("Sim, Adicionar")
    msg.button(QMessageBox.No).setText("Agora não")
    msg.setDefaultButton(QMessageBox.Yes)
    
    resposta = msg.exec_()
    
    if resposta == QMessageBox.Yes:
        script_path = Path(__file__).resolve().parent / "clipboard.py"
        
        # O sys.executable garante que ele usará o ambiente virtual atual (venv/uv) no boot
        python_path = Path(sys.executable).resolve()
        
        desktop_content = f"""[Desktop Entry]
Type=Application
Exec={python_path} {script_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Ubuntu Clipboard
Comment=Inicializar o histórico em background
Icon=edit-paste
"""
        with open(desktop_file, "w") as f:
            f.write(desktop_content)
            
        success_msg = QMessageBox()
        success_msg.setIcon(QMessageBox.Information)
        success_msg.setWindowTitle("Sucesso")
        success_msg.setText("Configurado com sucesso! Você pode remover futuramente usando o painel de 'Aplicativos Iniciais' do sistema.")
        success_msg.exec_()

if __name__ == "__main__":
    setup_autostart()
