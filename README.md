# Overwatch Card Game

Um web game inspirado no universo de cartas colecionáveis, desenvolvido com **Python + Flask**, onde o jogador abre pacotes, coleciona personagens e completa coleções para ganhar recompensas.

---

## 🚀 Sobre o projeto

O **Overwatch Card Game** é um projeto pessoal criado com o objetivo de praticar desenvolvimento web full stack, utilizando:

* Backend com **Flask (Python)**
* Frontend com **HTML, CSS e JavaScript**
* Informações internas em arquivos `.json`
* Persistência em banco de dados externo `sql`
  

O jogo simula a experiência de abrir pacotes de cartas, com diferentes raridades, progresso de coleção e sistema de recompensas.

---

## 🎮 Funcionalidades

* 🎁 Abertura de pacotes (comum, raro e eventos)
* 🎲 Sistema de sorteio com raridades
* 🧾 Inventário de cartas do jogador
* 📚 Sistema de coleções (sets)
* 🏆 Recompensas por completar coleções
* ⭐ Sistema de nível e experiência (XP)
* 🛒 Loja para compra de pacotes
* 🎨 Interface com animações (flip de cartas, abertura de pack)
* 🔐 Sistema de login e registro de usuários

---

## 📁 Estrutura do projeto

```
/data
    characters.json
    events.json
    icons.json
    packs.json
    sets.json

/static
    /css
    /images
    /logos
    /icons

/templates
    *.html

/sql
    /controller
    /repository

/routes
/services
/utils
```

---

## 🧠 Conceitos aplicados

Este projeto foi desenvolvido com foco em aprendizado, aplicando conceitos como:

* Organização de código em camadas (routes, services, utils)
* Manipulação de arquivos JSON como banco de dados
* Controle de sessão com Flask
* Sistema de progressão (XP e nível)
* Lógica de probabilidade (sorteio de cartas)
* Renderização dinâmica com Jinja2
* Responsividade e UI/UX

---

## ⚙️ Como rodar o projeto

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
pip install requirements.txt
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

## 🔮 Melhorias futuras

* ~~Sistema de raridades mais avançado~~
* Cartas especiais de eventos
* Sistema de marketplace entre jogadores
* Melhorias visuais e animações
* ~~Banco de dados real (SQLite ou PostgreSQL)~~

---

## 📌 Status do projeto

🚧 Em desenvolvimento contínuo

---

## 👨‍💻 Autor

Desenvolvido por Hetrisley Gomes, como projeto de aprendizado 💻🔥

---

## 📄 Licença

Este projeto é apenas para fins educacionais.
