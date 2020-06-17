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
With Postgres running, restore a database using my custom python script. From the folder in terminal run:
```bash
dropdb okr_test_local
createdb okr_test_local
flask db upgrade
python create_dummy_data.py
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
- Alternatively you can use my deployment `https://dnsvckvc-fsnd-okr.herokuapp.com/`
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
    - Pagination possible
    - Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
- Sample: `curl http://127.0.0.1:5000/persons`

```
{
  "persons": [
    {
      "first_name": "Max",
      "id": 1,
      "is_boss": false,
      "name": "Mustermann"
    },
    {
      "first_name": "Ali",
      "id": 2,
      "is_boss": false,
      "name": "Li"
    },
    {
      "first_name": "Maria",
      "id": 3,
      "is_boss": true,
      "name": "Mendez"
    }
  ],
  "success": true
}
```

#### GET '/objectives'
- General
    - Returns all objectives
    - Pagination possible
    - Request arguments: None
- Sample: `curl http://127.0.0.1:5000/objectives`
```
{
  "objectives": [
    {
      "complete_name": "Mustermann, Max",
      "description": "Be a good husband",
      "id": 1,
      "person": 1
    },
    {
      "complete_name": "Mustermann, Max",
      "description": "Be a good employee",
      "id": 2,
      "person": 1
    },
    {
      "complete_name": "Li, Ali",
      "description": "Be a good investor",
      "id": 3,
      "person": 2
    },
    {
      "complete_name": "Mendez, Maria",
      "description": "Be a good boss",
      "id": 4,
      "person": 3
    },
    {
      "complete_name": "Mustermann, Max",
      "description": "Do test driven development",
      "id": 5,
      "person": 1
    }
  ],
  "success": true
}
```
#### GET '/objectives/<int:objective_id>/requirements'
- General
    - Returns a set of requirements pertaining to the objective
    - Request arguments: pagination through URL parameters
- Sample: `curl http://127.0.0.1:5000/objectives/1/requirements`
```
{
  "requirements": [
    {
      "description": "Take out trash",
      "id": 1,
      "is_met": false,
      "objective_description": "Be a good husband",
      "objective_id": 1
    },
    {
      "description": "Buy flowers",
      "id": 2,
      "is_met": false,
      "objective_description": "Be a good husband",
      "objective_id": 1
    },
    {
      "description": "Say something nice each day",
      "id": 3,
      "is_met": false,
      "objective_description": "Be a good husband",
      "objective_id": 1
    }
  ],
  "success": true
}
```

#### POST '/objectives'
- General
    - allows to create new question or search existing ones depending on request body
    - Request arguments: json body
- Sample 1: `curl --header "Content-Type: application/json" --header "Authorization: Bearer <ACCESS_TOKEN>" -d '{'person': 1, 'objective': 'Do test driven development', 'requirements': 'Implement one test'}' -X POST http://127.0.0.1:5000/objectives`
```
{
  "n_requirements": 18,
  "objective_id": 9,
  "success": true
}
```

#### POST '/objectives/<int:objective_id>/requirements'
- General
    - allows to create new question or search existing ones depending on request body
    - Request arguments: json body
- Sample 1: `curl --header "Content-Type: application/json" --header "Authorization: Bearer <ACCESS_TOKEN>" -d '{'objective_id': 1,  'description': 'Accept new requirements'}' -X POST http://127.0.0.1:5000/objectives/1/requirements`
```
{
  "new_requirement_id": 16,
  "objective_id": 1,
  "success": true
}
```

#### PATCH '/requirements/<int:requirement_id>'
- General
    - allows to update the status of a requirement depending on whether it is met or not
    - Request arguments: json body
- Sample 1: `curl --header "Content-Type: application/json" --header "Authorization: Bearer <ACCESS_TOKEN>" -d '{'objective_id': 1,  'requirement_id': 1, 'is_met': true}' -X POST http://127.0.0.1:5000/requirements/1`
```
{
  "changed": true,
  "is_met": true,
  "previous_status": false,
  "success": true
}
```

#### DELETE '/objectives/<int:objective_id>'
- General
    - Allows to delete an objective by objective ID
- Sample: `curl -X DELETE http://127.0.0.1:5000/objectives/3` 

```
{
  "deleted_id": 3,
  "success": true
}
```

#### DELETE '/requirements/<int:requirement_id>'
- General
    - Allows to delete a requirement by requirement ID
    - Request arguments: json body
- Sample: `curl -X DELETE http://127.0.0.1:5000/requirements/15` 

```
{
  "deleted_id": 16,
  "success": true
}
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
