# Overwatch Card Game

***Overwatch Card Game*** is a browser-based collectible card game inspired by the universe of Overwatch. It is also a practical study in designing, developing, maintaining and evolving a real-world web application, covering game systems, databases, backend architecture, real-time communication, localization and application management.

# README in different languages
- [English](README.md)
- [Português](README.pt.md)

---

## About

Overwatch Card Game is a browser-based collectible card game inspired by the universe of Overwatch. The project combines card collection, deck building, packs, events, a player store and real-time PvP battles into a web application.

Beyond the game itself, this project serves as a practical study in the development and management of a real-world web application. Throughout its development, different approaches to frontend development, backend architecture, databases, authentication, localization, real-time communication and application organization have been explored and progressively refined.

The project is built with Python, Flask, JavaScript, HTML, CSS, PostgreSQL and Socket.IO, with the codebase organized into repositories, controllers and services to separate different responsibilities of the application.

The project is continuously used to experiment with development practices, architectural decisions, database design, game logic and the challenges involved in maintaining and evolving an application over time.

---

## Project Purpose

This project has two complementary purposes.

**Game development**: build a functional collectible card game with collection, deck building, economy, events and real-time player-versus-player battles.

**Web application study**: use the project as a practical environment for studying how a web application is designed, developed, maintained and progressively improved as its complexity increases.

Rather than being developed solely as a demonstration of a specific technology, the project is intentionally used to explore real development challenges and evaluate different technical and architectural decisions.

---

## Project structure

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

## Features

* Pack opening (common, rare, and event packs)
* Rarity-based draw system
* Player cards inventory
* Sets system
* Rewards for completing Sets
* Monthly and seasonal events
* Level and experience (XP) system
* Store for purchasing packs
* Avatar and site theme customization
* Animated interface
* User login and registration system

---

## Applied concepts

This project was developed with a focus on learning, applying concepts such as:

* Layered code organization (routes, services, utils)
* Database persistence
* Session management
* Authentication
* Sockets
* Progression system (XP and level)
* Probability logic (card drawing)
* Temporary events
* Client synchronization
* Responsiveness and UI/UX
* Internationalization
* Git and branching
* Maintenance/refactoring of existing code
  
---

## How to run the project

**Note:** When following the steps below, you will need to configure your own database.


1. Clone the repository:

```bash
git clone https://github.com/HetrisleyGomes/Overwatch-Card-Game.git
```

2. Navigate to the folder:

```bash
cd Overwatch-Card-Game
```

Optional: Set up a virtual environment
```bash
python -m venv .venv
```

And then activate it:
```bash
.\.venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Run the project:

```bash
python run.py
```

5. Access it in your browser:

```
http://localhost:5000
```

---

## Future improvements
* New variations of existing characters
* New characters
* New customization icons and themes
* Special event cards
* Player-to-player marketplace system
* Visual improvements and animations

---

## Project status

🚧 Under continuous development

---

## Author

Developed by Hetrisley Gomes as a learning project.

* Reading of the [web application management experience report](https://docs.google.com/document/d/1zfvDdwbaI8FGIw6DIiQ1ibbReLjf1vMRfOzJND49yk0/edit?usp=sharing "Acessar") - (Available only in Portuguese)

---

## Licence

This project is for educational purposes only.

**MIT License**

---

### Copyrights

© 2026 Overwatch-Card-Game — An independent, non-profit project developed for educational and entertainment purposes.

Overwatch, its characters, names, trademarks, and original visual elements are the property of Blizzard Entertainment. All rights belong to their respective owners.

The card artwork and variations presented in this project were developed independently, with no official affiliation with Blizzard. Some of the content was inspired by creations shared by community members, including Reddit users.

Please contact us regarding copyright inquiries or credit adjustments.