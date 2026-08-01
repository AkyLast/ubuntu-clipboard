# Manual Avançado de Usuário (UX/UI)

A engenharia por trás do **Ubuntu Clipboard** teve apenas um único norte: criar a Experiência do Usuário (UX) mais responsiva e fluida do ecossistema Linux. Não usamos cliques desnecessários e automatizamos o dimensionamento das informações para poupar seu tempo cognitivo.

## Navegando pelo Histórico

### Separação Inteligente
O app divide automaticamente o que você copia para que o seu histórico não se torne uma "sopa de caracteres":
- **Recentes**: Uma view aglomerada com as últimas 15 coisas que passaram pelo seu teclado. Útil para saltos rápidos de contexto (alt+tab).
- **Frases**: Strings minúsculas com menos de 100 caracteres. Textos de senhas ou pedaços curtos caem aqui e recebem uma limitação severa de altura para não roubar o seu espaço visual.
- **Texto**: *Snippets* gigantes, longos comandos bash, ou parágrafos de documentação (mais de 100 caracteres).
- **Imagens**: Exclusivo para *prints* e edições.
- **Favoritos**: A base de dados blindada de fragmentos recorrentes que não serão perdidos na reinicialização.

### O Algoritmo de Altura Dinâmica
Textos não são iguais. Na engenharia visual, um card de texto precisa respeitar proporções. 
- Se você copiou apenas `sudo apt update`, o card sofre corte na altura mínima (75 caracteres). 
- Mas se você tem um longo texto descritivo, o layout é instruído a "dobrar o tamanho máximo" (até 220 caracteres esticáveis) permitindo que você compreenda 3 ou 4 linhas contextuais na janela antes dele truncar. Isso reduz a necessidade desesperada de você tentar lembrar do começo e fim de um parágrafo que acabou de copiar.

### O Gerenciamento Híbrido de Imagens
Você sabia que um "Print Screen" na resolução 4K gera dados brutais na área de transferência? Para não engasgar o app com lentidão, criamos duas realidades de renderização:
- **No Aplicativo (A Visualização)**: Nós escalonamos fisicamente o buffer da sua foto 4k em uma miniatura fluida com Aspect Ratio preservado de até 120 pixels de altura, para exibição imediata e com extrema suavidade (*SmoothTransformation*).
- **No Sistema (O Clipboard Real)**: Apesar da miniatura otimizada na sua tela, quando você "Clica" para resgatar a foto, ele **não cola a miniatura**. Ele repassa 100% da resolução 4k original intocada para o seu aplicativo de destino.

## A Interação 

### O Sistema de Clique e Desaparecimento
1. **Botão Esquerdo (A Ação Absoluta)**: Você chama a janela (Super+V). Encontra a frase ou imagem desejada, basta um *Click* esquerdo simples no corpo do quadro negro do card de sua preferência. Magicamente, a janela se recolhe, devolve o foco para a sua aba de trabalho, injeta o texto/imagem direto no buffer da memória gráfica, pronto para você pressionar `Ctrl + V`. Rápido, preciso e indolor.
2. **Botão Direito (O Menu Tático)**: Clicar com o botão direito revela o Menu de Contexto (Context Menu). Foi criado para não poluir os seus cartões com ícones estranhos (como o tradicional ícone amarelo de estrela). Com ele, você salva permanentemente o objeto desejado na aba de **Favoritos** de forma silenciosa e limpa.

### Gestão do Lixo e Estado de Pânico
No canto superior direito, três ícones minúsculos guardam comandos muito importantes:
- **(✕) O Esconderijo**: Uma forma gentil de apenas recolher a janela. Ele é igual a você apenas clicar fora dela com o mouse.
- **(🗑) O Reset Profundo (A Lixeira)**: O sistema começou a ficar pesado pois você usou mais de 50 cópias hoje? Um toque na lixeira envia uma ordem para destruir e esvaziar todos os layouts na mesma hora, **limpando sua RAM e sua tela**, sem arrancar nenhum dos seus favoritos fixos do banco de dados.
- **(⏻) A Extinção do Daemon**: Manda um *kill-signal* para o processo em background. Destroi os soquetes e mata a aplicação. Ótimo caso você decida limpar qualquer traço da sua área de transferência recente antes de desligar o PC. Na próxima tentativa de atalho, você notará a tela não aparecendo pois o Daemon precisará de um tempo acordando de novo (A *Rule of Two*, ou o "Run Twice").
