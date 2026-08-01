# Arquitetura e Decisões Técnicas

Para alcançar o status de *Daemon* performático e de baixa latência, o **ubuntu-clipboard** precisou resolver problemas pesados de controle de concorrência, delegação de *Garbage Collection* e restrições de exibição do Linux (X11/Wayland).

## 0. Topologia do Projeto (Guia para Contribuidores)
A base de código foi desenhada usando *Separation of Concerns* (SoC) para que a lógica de negócio, a persistência e a interface gráfica não se misturem. Se você deseja alterar algo no projeto, guie-se por esta estrutura:

```text
ubuntu-clipboard/
├── Makefile                   # Painel de automação para devs (testes, linting, empacotamento).
├── clipboard.py               # Ponto de entrada (Wrapper principal).
├── setup_autostart.py         # Script interativo de configuração de boot (Gera .desktop).
├── tests/                     # Suíte de testes de integridade e comprovação de privacidade.
└── src/                       # O núcleo (Core) da aplicação.
    ├── clipboard_app.py       # Lógica do Daemon, Single Instance e IPC (Sockets).
    ├── database.py            # Camada de Persistência (SQLite3), lida com Favoritos e BLOBs.
    └── ui/                    # Tudo relacionado à renderização visual (PyQt5).
        ├── main_window.py     # Orquestrador da janela, detecção de atalhos e sistema de abas.
        └── components.py      # Widgets reutilizáveis (O formato dos cartões de itens).
```

## 1. O Padrão "Single Instance" via IPC
O maior desafio de atrelar um script Python a um atalho de teclado global (ex: `Super + V`) é que se o usuário pressionar o atalho nervosamente 5 vezes, o sistema operacional tentará iniciar 5 cópias gigantescas do interpretador Python e do Framework Qt. Isso faria a máquina travar instantaneamente.

Para blindar o sistema contra isso, empregamos uma abordagem robusta de *Inter-Process Communication* (IPC) em conjunto com o padrão *Single Instance*:

No arquivo `src/main.py`:
1. Quando o script `clipboard.py` é iniciado, ele tenta agir primeiramente como **Cliente**. Ele invoca o `QLocalSocket` e tenta conectar a um servidor local UNIX chamado `daemon_clipboard_ubuntu`.
2. Se ele conseguir conectar, a grande mágica acontece: significa que já existe um *Daemon* (motor) escondido na RAM. O nosso cliente atual escreve uma cadeia de bytes simplíssima (o comando `b"MOSTRAR"`) no socket e se autoencerra (`sys.exit(0)`).
3. Se ele **não** conseguir conectar, ele assume que é o primeiro a chegar. Imediatamente ele invoca o `QLocalServer`, passa a dominar o nome `daemon_clipboard_ubuntu` e inicia a interface invisível no background.
4. Quando o servidor recebe o pulso `b"MOSTRAR"`, ele executa nativamente as subrotinas da GUI (`show()`, `activateWindow()`, `raise_()`) em zero milissegundos.

## 2. Abstração do Banco de Dados Local (SQLite)
A introdução da persistência (Favoritos) gerou uma necessidade de *Storage*. Salvar textos e arquivos PNG espalhados numa pasta não é uma prática aprovada para sistemas de alta escalabilidade e organização.

A arquitetura resolveu isso injetando o `src/database.py`, que encapsula toda a ponte para o **SQLite3** nativo do Python:
- **Localização Padrão**: Segue o padrão estrito XDG Base Directory Specification em `~/.local/share/ubuntu-clipboard/favorites.db`.
- **Armazenamento de Imagens Híbrido**: Em vez de gerir paths de disco, as imagens são interceptadas cruas do sistema (`QPixmap`), transcodificadas instantaneamente em um buffer compactado (PNG) via `QByteArray` e `QBuffer`, e então empurradas para a tabela SQLite usando o tipo primitivo `BLOB`. A leitura e re-renderização da string de bytes de volta para imagem em tela ocorre em tempo constante.

## 3. Mitigação de Memory Leak e C++ nativo
Armazenar dezenas de `QPixmap` (telas, janelas capturadas em 4K, fotos grandes) arrebenta o heap de memória de qualquer sistema se não houver um *Garbage Collector* agressivo.

O motor da nossa UI não apenas expulsa os itens antigos dos Arrays visuais quando o limite é atingido; ele garante a varrição de memória. Optamos deliberadamente por evitar scripts nativos complexos em C, invocando em vez disso o comando `widget.deleteLater()`. Esta é a API direta do PyQt que envia o Widget (e todos os seus ponteiros pesados de imagem) para a fila de eventos do **núcleo C++ do Qt**, onde os ponteiros brutos são destruídos em nível de micro-instruções, proporcionando performance nativa C de forma transparente para o desenvolvedor Python.

## 4. O By-pass Seguro do Wayland
Sistemas Ubuntu modernos usam **Wayland**. Um dos pilares de segurança do Wayland é que janelas que não têm o foco primário na tela são estritamente proibidas de ver o que entra na Área de Transferência. Isso mataria nosso *Daemon*.

No arquivo de inicialização, realizamos o seguinte resgate tático ambiental:
```python
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"
```
A primeira diretiva obriga o aplicativo a conversar com o XWayland (a camada de compatibilidade legacy), garantindo leitura irrestrita do *clipboard* sem violar os isolamentos hard do servidor de vídeo primário. A segunda diretiva silencia os ruídos agressivos que o motor emite no terminal quando confrontado com essa decisão (ex: *"Warning: Ignoring XDG_SESSION_TYPE=wayland"*), garantindo logs puros.
