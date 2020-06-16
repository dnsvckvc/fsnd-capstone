import unittest
import json

from flask_sqlalchemy import SQLAlchemy

from okr import create_app
from models import setup_db, Person, Objective, Requirement

# Bearer Tokens for RBAC
# Without Token no endpoint can be accessed!

"""Get bearer tokens from file"""

# Boss can do everything
with open('boss_jwt.txt', 'r') as file:
    AUTHORIZATION_BOSS = file.read().replace('\n', '')

# print(AUTHORIZATION_BOSS)

# employee can get everything and patch requirement
with open('employee_jwt.txt', 'r') as file:
    AUTHORIZATION_EMPLOYEE = file.read().replace('\n', '')

# Format tokens into headers
HEADER_BOSS = headers = {
            'Authorization': 'Bearer {}'.format(AUTHORIZATION_BOSS)
        }

HEADER_EMPLOYEE = headers = {
            'Authorization': 'Bearer {}'.format(AUTHORIZATION_EMPLOYEE)
        }


""" Start of Test Class """


class OKRTestCase(unittest.TestCase):
    """This class represents the OKR test case"""

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.database_name = "okr_test_local"
        self.database_path = "postgresql://{}/{}".format('localhost:5432',
                                                         self.database_name)
        setup_db(self.app, self.database_path)

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

    def tearDown(self):
        """Execute after each test"""
        pass

    """
    Endpoints will include at least…
    Two GET requests
    One POST request
    One PATCH request
    One DELETE request
    """

    # All of the following tests with full access Boss tokens

    def test_get_paginated_persons(self):
        res = self.client.get('/persons', headers=HEADER_BOSS)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['persons']))

    def test_404_persons_beyond_valid_page(self):
        res = self.client.get('/persons?page=100', headers=HEADER_BOSS)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_paginated_objectives(self):
        res = self.client.get('/objectives', headers=HEADER_BOSS)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['objectives']))

    def test_404_objectives_beyond_valid_page(self):
        res = self.client.get('/objectives?page=100', headers=HEADER_BOSS)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_requirements_by_objective(self):
        res = self.client.get('/objectives/1/requirements',
                              headers=HEADER_BOSS)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['requirements']))

    def test_404_beyond_objective(self):
        res = self.client.get('/objectives/1000/requirements',
                              headers=HEADER_BOSS)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # delete
    # no one can delete persons

    # only boss can delete objectives --> will also delete requirements
    # only boss can delete requirement --> what when no requirements left

    def test_delete_objective_successful(self):
        res = self.client.delete('/objectives/2', headers=HEADER_BOSS)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_id'], 2)

    def test_delete_objective_fail(self):
        res = self.client.delete('/objectives/1000', headers=HEADER_BOSS)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_requirement_successful(self):
        res = self.client.delete('/requirements/7', headers=HEADER_BOSS)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_id'], 7)

    def test_delete_requirement_fail(self):
        res = self.client.delete('/requirements/1000', headers=HEADER_BOSS)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # patch
    # person can patch if finished or not
    # so can boss                           --> one function to update status

    def test_patch_requirement_successful(self):
        update_data = {
            'objective_id': 1,
            'requirement_id': 1,
            'is_met': True
        }
        res = self.client.patch('requirements/1', json=update_data,
                                headers=HEADER_BOSS)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['is_met'], True)
        self.assertEqual(data['changed'], True)

    def test_patch_requirement_no_change(self):
        update_data = {
            'objective_id': 1,
            'requirement_id': 2,
            'is_met': False
        }
        res = self.client.patch('requirements/2', json=update_data,
                                headers=HEADER_BOSS)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['is_met'], False)
        self.assertEqual(data['changed'], False)

    def test_patch_requirement_malformed(self):
        update_data = {
            'random': 1,
        }
        res = self.client.patch('requirements/1', json=update_data,
                                headers=HEADER_BOSS)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'request body malformed')

    # post
    # boss can post new objective     --> harder needs also requirements
    # boss can post new requirement   --> easier do first

    def test_post_new_requirement(self):
        new_requirement = {
            'objective_id': 1,
            'description': 'Accept new requirements'
        }

        all_requirements_pre = Requirement.query.filter(
            Requirement.objective == 1).all()

        res = self.client.post('/objectives/1/requirements',
                               json=new_requirement, headers=HEADER_BOSS)
        data = json.loads(res.data)

        all_requirements_post = Requirement.query.filter(
            Requirement.objective == 1).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(all_requirements_post) -
                         len(all_requirements_pre), 1)

    def test_post_new_requirement_malformed(self):
        new_requirement = {
            'objective': 1,
        }

        all_requirements_pre = Requirement.query.filter(
            Requirement.objective == 1).all()

        res = self.client.post('/objectives/1/requirements',
                               json=new_requirement, headers=HEADER_BOSS)
        data = json.loads(res.data)

        all_requirements_post = Requirement.query.filter(
            Requirement.objective == 1).all()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(len(all_requirements_post) -
                         len(all_requirements_pre), 0)

    def test_post_new_objective_single_successful(self):
        new_objective = {
            'person': 1,
            'objective': 'Do test driven development',
            'requirements': 'Implement one test'
        }

        all_objectives_pre = Objective.query.all()

        res = self.client.post('/objectives', json=new_objective,
                               headers=HEADER_BOSS)
        data = json.loads(res.data)

        all_objectives_post = Objective.query.all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(all_objectives_post) -
                         len(all_objectives_pre), 1)

    def test_post_new_objective_fail(self):
        new_objective = {
            'objective_typo': 'Do better test driven development',
            'requirements': [{'description:': 'Implement one test'},
                             {'description': 'Implement two tests'}]
        }

        all_objectives_pre = Objective.query.all()

        res = self.client.post('/objectives', json=new_objective,
                               headers=HEADER_BOSS)
        data = json.loads(res.data)

        all_objectives_post = Objective.query.all()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(len(all_objectives_post) -
                         len(all_objectives_pre), 0)

    """
    One test for success behavior of each endpoint
    One test for error behavior of each endpoint
    At least two tests of RBAC for each role
    """
    # All of the following tests test for correct access token behavior

    def test_get_paginated_persons_employee(self):
        res = self.client.get('/persons', headers=HEADER_EMPLOYEE)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['persons']))

    def test_401_no_credentials_persons(self):
        res = self.client.get('/persons?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_get_paginated_objectives_employee(self):
        res = self.client.get('/objectives', headers=HEADER_EMPLOYEE)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['objectives']))

    def test_401_no_credentials_objectives(self):
        res = self.client.get('/objectives?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_get_requirements_by_objective_employee(self):
        res = self.client.get('/objectives/1/requirements',
                              headers=HEADER_EMPLOYEE)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['requirements']))

    def test_401_no_credentials_requirements(self):
        res = self.client.get('/objectives/1/requirements')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    # patch test, works with employee headers too

    def test_patch_requirement_successful_employee(self):
        update_data = {
            'objective_id': 1,
            'requirement_id': 2,
            'is_met': True
        }
        res = self.client.patch('requirements/2', json=update_data,
                                headers=HEADER_EMPLOYEE)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['is_met'], True)
        self.assertEqual(data['changed'], True)

    def test_patch_requirement_no_header(self):
        update_data = {
            'objective_id': 1,
            'requirement_id': 2,
            'is_met': True
        }
        res = self.client.patch('requirements/2', json=update_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Headers not present.')

    # all tests that succeed only with boss headers

    def test_delete_objective_no_permission(self):
        res = self.client.delete('/objectives/3',
                                 headers=HEADER_EMPLOYEE)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],
                         'User does not have these permissions.')

    def test_delete_objective_no_header(self):
        res = self.client.delete('/objectives/3')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Headers not present.')

    def test_delete_requirement_fail_no_permission(self):
        res = self.client.delete('/requirements/8', headers=HEADER_EMPLOYEE)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],
                         'User does not have these permissions.')

    def test_delete_requirement_fail_no_headers(self):
        res = self.client.delete('/requirements/8')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Headers not present.')

    def test_post_new_requirement_no_permission(self):
        new_requirement = {
            'objective_id': 1,
            'description': 'Accept new requirements'
        }

        all_requirements_pre = Requirement.query.filter(
            Requirement.objective == 1).all()

        res = self.client.post('/objectives/1/requirements',
                               json=new_requirement, headers=HEADER_EMPLOYEE)
        data = json.loads(res.data)

        all_requirements_post = Requirement.query.filter(
            Requirement.objective == 1).all()

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],
                         'User does not have these permissions.')
        self.assertEqual(len(all_requirements_post) -
                         len(all_requirements_pre), 0)

    def test_post_new_requirement_no_headers(self):
        new_requirement = {
            'objective_id': 1,
            'description': 'Accept new requirements'
        }

        all_requirements_pre = Requirement.query.filter(
            Requirement.objective == 1).all()

        res = self.client.post('/objectives/1/requirements',
                               json=new_requirement)
        data = json.loads(res.data)

        all_requirements_post = Requirement.query.filter(
            Requirement.objective == 1).all()

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Headers not present.')
        self.assertEqual(len(all_requirements_post) -
                         len(all_requirements_pre), 0)

    def test_post_new_objective_no_permission(self):
        new_objective = {
            'person': 1,
            'objective': 'Do test driven development',
            'requirements': 'Implement one test'
        }

        all_objectives_pre = Objective.query.all()

        res = self.client.post('/objectives', json=new_objective,
                               headers=HEADER_EMPLOYEE)
        data = json.loads(res.data)

        all_objectives_post = Objective.query.all()

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],
                         'User does not have these permissions.')
        self.assertEqual(len(all_objectives_post) -
                         len(all_objectives_pre), 0)

    def test_post_new_objective_no_headers(self):
        new_objective = {
            'person': 1,
            'objective': 'Do test driven development',
            'requirements': 'Implement one test'
        }

        all_objectives_pre = Objective.query.all()

        res = self.client.post('/objectives',
                               json=new_objective)
        data = json.loads(res.data)

        all_objectives_post = Objective.query.all()
        self.assertEqual(res.status_code, 401)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Headers not present.')
        self.assertEqual(len(all_objectives_post)-len(all_objectives_pre), 0)


# Make tests conveniently executable
if __name__ == "__main__":
    unittest.main()
