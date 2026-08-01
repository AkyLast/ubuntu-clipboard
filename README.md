# Ubuntu Clipboard

Um gerenciador de área de transferência assíncrono e independente para ecossistemas Linux (com suporte primário ao GNOME/Wayland). Ele substitui o tradicional "Super + V" do Windows com uma arquitetura modular em Python (PyQt5) voltada para **estabilidade, baixa latência e respeito total à sua privacidade**.

---

## 📌 Por que não usar as extensões padrão do GNOME?

O ecossistema GNOME depende pesadamente do GJS (GNOME JavaScript) que roda atrelado ao `Mutter` (o compositor de janelas principal). Históricos de área de transferência nativos do GNOME carregam imagens brutas e textos diretamente nessa thread principal. 
O resultado? **Vazamentos de memória (Memory Leaks)** severos e travamentos na interface do usuário após dias de máquina ligada.

O **Ubuntu Clipboard** foi desenhado como um aplicativo independente (um *Daemon*) que vive totalmente fora do escopo do GNOME, resolvendo o problema de performance pela raiz.

---

## 🧠 Arquitetura Core: A Regra do "Run Twice" (Daemon vs UI)

Para garantir que o seu histórico apareça **instantaneamente** na tela ao pressionar um atalho, o aplicativo adota o padrão de projeto *Single Instance* (Instância Única) através de Comunicação Inter-Processos (IPC).

Isso introduz o conceito mais importante deste software: **A separação entre o Motor (Daemon) e a Interface (UI).**

1. **A Primeira Execução (O Despertar do Daemon)**:
   Quando você roda o comando `clipboard.py` pela primeira vez, **nenhuma janela aparecerá na tela**. Neste momento, o script silenciosamente se aloja na memória (em background), cria um servidor IPC e começa a "escutar" invisivelmente tudo o que você copia no sistema.
   
2. **A Segunda Execução em diante (O Disparo da Interface)**:
   Ao rodar o comando pela segunda vez, o novo processo percebe que o "Motor" já está rodando. Ele então funciona apenas como um "mensageiro": dispara um ping (`b"MOSTRAR"`) para o Motor e se autodestrói. O Motor recebe o ping e faz a janela visual pular na tela em milissegundos.

**Solução Prática**: Para que você nunca precise se preocupar com a "primeira execução" silenciosa, o projeto conta com um script de **Autostart** (veja na Instalação) que liga o Motor automaticamente assim que o seu Linux faz o boot!

---

## 🔒 Privacidade Híbrida

Lidar com a sua área de transferência é um assunto delicado. Você copia senhas, chaves SSH e tokens de API o tempo todo. 
- **O Histórico Padrão é 100% Volátil**: Tudo o que vai para as abas *Recentes*, *Textos* e *Imagens* reside puramente na sua memória RAM. Ao reiniciar o computador ou encerrar o Daemon (botão ⏻), esses dados desaparecem para sempre. Nenhuma senha sua é gravada no disco rígido.
- **Favoritos Seguros (SQLite)**: Quer salvar um snippet de código para sempre? Clique com o Botão Direito nele e escolha "Favoritar". Somente (e estritamente) esses itens escolhidos a dedo por você são persistidos de forma estruturada em um banco de dados local (`favorites.db`).

---

## 🛠️ Como Instalar e Rodar

1. **Clone o Repositório e Instale as dependências:**
   ```bash
   git clone https://github.com/seu-usuario/ubuntu-clipboard.git
   cd ubuntu-clipboard
   
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Gere a Configuração de Inicialização (Opcional, porém Altamente Recomendado):**
   ```bash
   python3 setup_autostart.py
   ```
   *Um assistente gráfico pedirá permissão para configurar o aplicativo para iniciar com o sistema (ligando o Daemon no boot).*

3. **Inicie o App (Ou crie o atalho global)**
   ```bash
   python3 clipboard.py
   ```

Para aprender a vincular esse comando ao atalho `Super + V` no GNOME, leia a [Documentação de Instalação](docs/instalacao.md).

---

## 📖 Documentações

A arquitetura da pasta [docs/](docs/):
- [Introdução (O Problema Wayland vs GNOME)](docs/introducao.md)
- [Instalação Definitiva e Atalhos Globais](docs/instalacao.md)
- [Arquitetura Interna e Sockets IPC](docs/arquitetura.md)
- [Manual de Uso e UX (User Experience)](docs/uso.md)
