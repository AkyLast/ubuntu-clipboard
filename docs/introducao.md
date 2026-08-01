# Introdução ao Problema

O **Ubuntu Clipboard** não é apenas mais um gerenciador visual; ele é uma resposta de engenharia de software aos problemas clássicos de gestão de memória e segurança do Desktop Linux contemporâneo.

## O Calcanhar de Aquiles das Extensões GNOME

A maioria dos usuários de Ubuntu/GNOME recorre a extensões instaladas pelo navegador para obter funcionalidades de clipboard. No entanto, essas extensões são scripts em **GJS (GNOME JavaScript)**. 

No GNOME, todo código GJS das extensões roda na **mesma thread** do `Mutter` (o compositor e gerenciador de janelas). Se você copia 50 imagens pesadas, o GJS precisa alocar essas imagens em sua memória primária. O Garbage Collector (Coletor de Lixo) do JavaScript nativo do GNOME é notoriamente conservador. O resultado é inevitável: com o passar dos dias, a interface inteira do seu sistema operacional começa a sofrer gargalos de renderização (*stutters*) por culpa de um simples histórico de "copiar e colar".

## A Abordagem "Daemon Python + Qt"

Para blindar o sistema operacional contra vazamentos de memória, este projeto removeu a responsabilidade de dentro da *shell* do GNOME.
Nós transformamos o histórico em um processo independente (`clipboard.py`), que adota as seguintes premissas:

1. **Processo Desacoplado**: Se, por qualquer motivo, o nosso software consumir 2GB de RAM porque você copiou milhares de fotos 4K, **o seu sistema continuará fluido**. Apenas o processo isolado do Python estará pesado. E com um único clique no botão de "Lixeira" nativo do nosso app, essa memória volta instantaneamente para o sistema graças à destruição de ponteiros em nível C++.
2. **Interface Rápida e Imutável**: O uso da biblioteca Qt5 garante renderização com aceleração de hardware, alinhamento perfeito de pixels e menus responsivos (ao contrário das caixas de CSS às vezes desajeitadas do GTk4/GJS customizado).

## O Fantasma do Wayland

O protocolo moderno do Linux (Wayland) foi construído sob uma forte premissa de segurança: "Aplicativos em segundo plano não têm permissão para saber o que você copia". Isso quebra qualquer ferramenta de clipboard.
A nossa arquitetura contorna essa limitação forçando, de maneira cirúrgica e segura, o protocolo de retrocompatibilidade do servidor de exibição. Explicamos o código técnico responsável por isso na sessão de [Arquitetura](arquitetura.md).

## O Respeito aos seus Dados

Para resolver o dilema entre *Conveniência vs Segurança*, dividimos o armazenamento:
- **Fluxo Volátil (Padrão)**: Todos os seus itens recentes vivem **apenas na memória RAM**. Um reboot ou o encerramento do processo é o suficiente para que tudo seja apagado permanentemente. O seu SSD nunca saberá que você copiou a sua senha.
- **Fluxo Persistente (Favoritos)**: Para as coisas que realmente importam (aquele comando Bash longo que você não quer digitar de novo), introduzimos os **Favoritos**. Mediante uma **ação explícita** do usuário (clique com o botão direito -> Favoritar), os dados saem da RAM volátil e são ancorados em um banco de dados estruturado SQLite 3, local e seguro.
