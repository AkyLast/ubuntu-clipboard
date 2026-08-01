# Instalação e Configuração

O Ubuntu Clipboard Uma ferramenta que afeta seu fluxo diário de trabalho precisa de uma instalação limpa e segura no seu sistema. 

## 1. Pré-requisitos
Certifique-se de ter as ferramentas base do Python e da biblioteca gráfica instaladas a nível de sistema operacional. Para o Ubuntu:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-pyqt5
```

## 2. Clonando e Preparando o Ambiente (venv)
Vamos colocar a aplicação na sua pasta de projetos e usar o `venv` padrão do Python:

```bash
git clone https://github.com/seu-usuario/ubuntu-clipboard.git
cd ubuntu-clipboard

# Cria e ativa um ambiente Python (venv)
python3 -m venv venv
source venv/bin/activate

# Instala as dependências da biblioteca
pip install -r requirements.txt
```

## 3. Configurando a Partida Instantânea (O Script de Autostart)
Conforme explicado detalhadamente na arquitetura, nosso app precisa de um processo "Invisível" correndo no fundo (Daemon) para funcionar em tempo real. Se você não configurá-lo no boot, terá que executar o atalho de teclado duas vezes ao ligar a máquina.

Para resolver isso, criamos o instalador assistido:
```bash
python3 setup_autostart.py
```
**O que ele faz?** Ele invoca uma pequena janela de diálogo pedindo permissão explícita para o seu usuário. Se você aceitar, ele vai lá na pasta central do sistema (`~/.config/autostart/`) e forja um arquivo chamado `.desktop`. Esse arquivo ensina o sistema operacional a ativar o Daemon automaticamente sem exibir a janela visual de imediato. A partir de amanhã, quando ligar o PC, basta um único "Ctrl+C" para que a mágica aconteça por debaixo dos panos.

## 4. O Atalho Global Infalível (Super + V)
O projeto ganha vida de verdade quando amarrado a um atalho físico.

1. Abra as **Configurações** gerais do GNOME/Ubuntu.
2. Navegue até a aba **Teclado**.
3. Vá em **Ver e Personalizar Atalhos** > **Atalhos Personalizados**.
4. Adicione o seu novo superpoder:
   - **Nome**: Ubuntu Clipboard
   - **Comando**: Aponte para o binário do python no venv e depois para o `clipboard.py`, ex: `~/ubuntu-clipboard/venv/bin/python3 ~/ubuntu-clipboard/clipboard.py` (Substitua os caminhos pelo seu diretório real onde clonou).
   - **Atalho**: Recomendamos fortemente a combinação `Super + V`.
