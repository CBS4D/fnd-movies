# Movie Flask API
## User level segregation and CRUD operations on movie dataset.

**APP LINK** - https://fnd-movies.herokuapp.com/api/v1/movies

To create admin user please first generate an admin key and then using that key create an admin account.

- generate admin key
- use admin key while creating admin account
- only admin user can perform CRUD operations on dataset.
- to create basic user account pass same info except admin key

## Search dataset

- One can search for a movie using - movie name, director name, rating, popularity and genre options.
## Tech

- Flask - Restful
- SQLAlchemy
- Marshmallow
- Flask-jwt-extended
- PostgrSQL

## Installation

requires [Python](https://www.python.org/) v3.6+ to run.

Create Virtual environment and install the dependencies and start the server.

```sh
python -m venv (virtual environment name)
```

```sh
pip install -r requirements.txt
```
Then start app
```sh
python main.py
```
