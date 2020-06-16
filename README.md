# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

## Database Setup
With Postgres running, restore a database using my custom python script. From the backend folder in terminal run:
```bash
sdfds
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

Then make sure to have all environment variables set.

```bash
export DATABASE_URL=postgresql://localhost:5432/okr_test_local
export FLASK_APP=okr
export FLASK_ENV=development
export AUTH0_DOMAIN=vckvc.eu.auth0.com
export ALGORITHMS=RS256
export API_AUDIENCE=okr
```

To run the server, execute (partially already step above):

```bash
export FLASK_APP=okr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `okr` directs flask to use the `okr` directory and the `__init__.py` file to find the application. 

## API Reference

### Getting Started
- Base URL: can only be run locally and is at `http://127.0.0.1:5000/`.
- Authentication: all endpoints require JWT Bearer toeksn with RBAC

### Error Handling

Errors are returned as JSON objects in the following format

```
{
    "success": False,
    "error": 422,
    "message": 'request body malformed'
}
```

### Endpoints
#### GET '/persons'
- General
    - Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
    - Request Arguments: None
    - Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
- Sample: `curl http://127.0.0.1:5000/persons`

```

```

#### GET '/objectives'
- General
    - Returns all objectives
    - Request arguments: category ID in request URL
- Sample: `curl http://127.0.0.1:5000/objectives`
```

```
#### GET '/objectives/<int:objective_id>/requirements'
- General
    - Returns a set of requirements pertaining to the objective
    - Request arguments: pagination through URL parameters
- Sample: `curl http://127.0.0.1:5000/questions?page=2`
```
```

#### POST '/questions'
- General
    - allows to create new question or search existing ones depending on request body
- Sample 1: `curl --header "Content-Type: application/json" -d '{"question": "what are you?", "answer":"hi", "category":"1", "difficulty":"1"}' -X POST http://127.0.0.1:5000/questions`
```
{
  "new_question_id": 25, 
  "success": true, 
  "total_questions": 19
}
```

#### DELETE '/questions/<int:quesiton_id>'
- General
    - Allows to delete an objective by objective ID
- Sample: `curl -X DELETE http://127.0.0.1:5000/objectives/1` 
```

```


## Testing
To run the tests, run
```
dropdb okr_test_local
createdb okr_test_local
flask db upgrade
python create_dummy_data.py
python test_okr.py
```

or even better

```
bash run_tests.sh
```
