# Flashy


## Introduction
Flashy is a web application to assist in studying . Flashy allows for the creation, organization, and studying of flashcards and flashcard decks. Users can also import and export flashcard decks as `.json` files.

Flashy brings two modes of studying, with “flip mode” and “written mode”. In flipped mode, users are shown the front side of a flashcard, then are prompted with a question asking if they know the definition of the item on the flashcard. In write mode, users are shown the front side of a flashcard, then are given a field to enter the definition. 

As users study, their confidence scores will adjust, serving as an approximate measure of their progress.

---

## Tech Stack

- **Back-end**: Python, Flask, Peewee, pytest, Flask-Login, python-dotenv
- **Front-end**: HTML, CSS, JavaScript, Jinja2
- **Deployment**: Render

---

## Online Access

Flashy is currently hosted online via Render.

Visit https://citflashcard.onrender.com/

---

## Setup Locally

1. Clone the repo

```
git clone https://github.com/yourusername/CITFlashcard.git
```

```
cd CITFlashcard
```

2. Create and activate virtual environment

```
py -3 -m venv venv
```

```
source venv/bin/activate
```

3. Install dependencies

```
pip install -r requirements.txt
```

4. Run the app

```
flask run
```

The web-app can now be locally accessed at http://127.0.0.1:5000 as long as the flask server is active.

---

## Contributors
 - Enock Lian
 - Bareera Leghari
 - Mekhai Patmore
 - Tyler West
 - Will Zhang