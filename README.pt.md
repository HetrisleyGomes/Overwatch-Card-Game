# Overwatch Card Game

***Overwatch Card Game*** é um jogo de cartas colecionáveis ​​para navegador inspirado no universo de Overwatch. É também um estudo prático sobre o design, desenvolvimento, manutenção e evolução de uma aplicação web do mundo real, abrangendo sistemas de jogo, bancos de dados, arquitetura de backend, comunicação em tempo real, localização e gerenciamento da aplicação.

# README em diferentes idiomas
- [English](README.md)
- [Português](README.pt.md)

---

## Sobre

O Overwatch Card Game é um jogo de cartas colecionáveis ​​baseado em navegador, inspirado no universo de Overwatch. O projeto combina coleta de cartas, construção de baralhos, pacotes, eventos, uma loja para jogadores e batalhas PvP em tempo real em uma única aplicação web.

Além do jogo em si, este projeto serve como um estudo prático sobre o desenvolvimento e o gerenciamento de uma aplicação web do mundo real. Ao longo de seu desenvolvimento, diferentes abordagens para o desenvolvimento de frontend, arquitetura de backend, bancos de dados, autenticação, localização, comunicação em tempo real e organização da aplicação foram exploradas e progressivamente refinadas.

O projeto foi desenvolvido utilizando Python, Flask, JavaScript, HTML, CSS, PostgreSQL e Socket.IO, com a base de código organizada em repositórios, controladores e serviços para separar as diferentes responsabilidades da aplicação.

O projeto é utilizado continuamente para experimentar práticas de desenvolvimento, decisões arquiteturais, modelagem de banco de dados, lógica de jogo e os desafios envolvidos na manutenção e evolução de uma aplicação ao longo do tempo.

---

## Proposito do Projeto

Este projeto tem dois objetivos complementares.

**Desenvolvimento de jogos**: criar um jogo de cartas colecionáveis ​​funcional, com sistemas de coleção, construção de baralhos, economia, eventos e batalhas jogador contra jogador em tempo real.

**Estudo de aplicações web**: utilizar o projeto como um ambiente prático para estudar como uma aplicação web é projetada, desenvolvida, mantida e aprimorada progressivamente à medida que sua complexidade aumenta.

Em vez de ser desenvolvido apenas como uma demonstração de uma tecnologia específica, o projeto é utilizado intencionalmente para explorar desafios reais de desenvolvimento e avaliar diferentes decisões técnicas e arquiteturais.

---

## Estrutura do Projeto

```
Overwatch-Card-Game
│
├── data/
├── routes/
│   ├── routes.py
│   └── routescombate.py
├── services/
├── sql/
│   ├── controller/
│   └── repositories/
├── static/
│   ├── extras
│   ├── font
│   ├── icons
│   ├── images
│   ├── logos
│   └── styles
├── templates/
├── translate/
├── utils/
│
├── config.py
├── server.py
└── run.py
```

---

## Funcionalidades

* Abertura de pacotes (comuns, raros e de eventos)
* Sistema de sorteio baseado na raridade
* Inventário de cartas de jogadores
* Sistema de coleções
* Recompensas por completar coleções
* Eventos mensais e sazonais
* Sistema de nível e experiência (XP)
* Loja para compra de pacotes
* Personalização de avatar e tema do site
* Interface com animações
* Sistema de login e cadastro de usuários

---

## Conceitos Aplicados

Este projeto foi desenvolvido com foco em aprendizado, aplicando conceitos como:

* Organização de código em camadas (routes, services, utils)
* Persistência de dados em banco de dados
* Controle de sessão
* Autenticação
* Sockets
* Sistema de progressão (XP e nível)
* Lógica de probabilidade (sorteio de cartas)
* Eventos temporários
* Sincronização entre clientes
* Responsividade e UI/UX
* internacionalização
* Git e branches
* Manutenção/refatoração de código existente

---

## Como rodar o projeto

**Atenção:** Ao realizar as etapas abaixo, você deverá configurar o seu próprio banco de dados.


1. Clone o repositório:

```bash
git clone https://github.com/HetrisleyGomes/Overwatch-Card-Game.git
```

2. Acesse a pasta:

```bash
cd Overwatch-Card-Game
```

Opcional: Instale um ambiente virtual
```bash
python -m venv .venv
```

E então ative-o:
```bash
.\.venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Execute o projeto:

```bash
python run.py
```

5. Acesse no navegador:

```
http://127.0.0.1:5000
```

---

## Melhorias futuras
* Novas variações de personagens existêntes
* Novos personagens
* Novos ícones e temas de customização
* Cartas especiais de eventos
* Sistema de marketplace entre jogadores
* Melhorias visuais e animações

---

## Status do projeto

🚧 Em desenvolvimento contínuo

---

## Autor

Desenvolvido por Hetrisley Gomes, como projeto de aprendizado

* Leitura do [relatório de experiência em gerenciamento de aplicação web](https://docs.google.com/document/d/1zfvDdwbaI8FGIw6DIiQ1ibbReLjf1vMRfOzJND49yk0/edit?usp=sharing "Acessar")

---

## Licença

Este projeto é apenas para fins educacionais.

**MIT License**

---

### Copyrights

© 2026 Overwatch-Card-Game — Projeto independente e sem fins lucrativos, desenvolvido para fins educacionais e de entretenimento.

Overwatch, seus personagens, nomes, marcas e elementos visuais originais são propriedade da Blizzard Entertainment. Todos os direitos pertencem aos seus respectivos detentores.

As artes e variações de cartas apresentadas neste projeto foram desenvolvidas de forma independente, sem vínculo oficial com a Blizzard. Parte do conteúdo foi inspirada em criações compartilhadas por membros da comunidade, incluindo usuários do Reddit.

Para solicitações relacionadas a direitos autorais ou ajustes de créditos, entre em contato.