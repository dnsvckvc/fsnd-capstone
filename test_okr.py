import unittest
import json

from flask_sqlalchemy import SQLAlchemy

from okr import create_app
from models import setup_db, Person, Objective, Requirement

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


    def test_get_paginated_persons(self):
        res = self.client.get('/persons')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['persons']))

    def test_404_persons_beyond_valid_page(self):
        res = self.client.get('/persons?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_get_paginated_objectives(self):
        res = self.client.get('/objectives')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['objectives']))

    def test_404_objectives_beyond_valid_page(self):
        res = self.client.get('/objectives?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_requirements_by_objective(self):
        res = self.client.get('/objectives/1/requirements')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['requirements']))

    def test_beyond_objective(self):
        res = self.client.get('/objectives/1000/requirements')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    # delete
    # no one can delete persons

    # only boss can delete objectives --> will also delete requirements
    # only boss can delete requirement --> what when no requirements left

    def test_delete_objective_successful(self):
        res = self.client.delete('/objectives/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_id'], 2)

    def test_delete_objective_fail(self):
        res = self.client.delete('/objectives/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_requirement_successful(self):
        res = self.client.delete('/requirements/7')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_id'], 7)

    def test_delete_requirement_fail(self):
        res = self.client.delete('/requirements/1000')
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
        res = self.client.patch('requirements/1', json = update_data)
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
        res = self.client.patch('requirements/2', json = update_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['is_met'], False)
        self.assertEqual(data['changed'], False)

    def test_patch_requirement_malformed(self):
        update_data = {
            'random': 1,
        }
        res = self.client.patch('requirements/1', json = update_data)
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

        all_requirements_pre = Requirement.query.filter(Requirement.objective == 1).all()

        res = self.client.post('/objectives/1/requirements', json = new_requirement)
        data = json.loads(res.data)

        all_requirements_post = Requirement.query.filter(Requirement.objective == 1).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(all_requirements_post)-len(all_requirements_pre), 1)


    def test_post_new_requirement_malformed(self):
        new_requirement = {
            'objective': 1,
        }

        all_requirements_pre = Requirement.query.filter(Requirement.objective == 1).all()

        res = self.client.post('/objectives/1/requirements', json = new_requirement)
        data = json.loads(res.data)

        all_requirements_post = Requirement.query.filter(Requirement.objective == 1).all()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(len(all_requirements_post)-len(all_requirements_pre), 0)

    def test_post_new_objective_single_successful(self):
        new_objective = {
            'person': 1,
            'objective': 'Do test driven development',
            'requirements': 'Implement one test'
        }

        all_objectives_pre = Objective.query.all()

        res = self.client.post('/objectives', json = new_objective)
        data = json.loads(res.data)

        all_objectives_post = Objective.query.all()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(all_objectives_post) - len(all_objectives_pre), 1)

    # def test_post_new_objective_multi_successful(self):
    #     new_objective = {
    #         'person': 1,
    #         'objective': 'Do better test driven development',
    #         'requirements': [{'description:': 'Implement one test'},
    #                             {'description': 'Implement two tests'}]
    #     }

    #     all_objectives_pre = Objective.query.all()

    #     res = self.client.post('/objectives', json = new_objective)
    #     data = json.loads(res.data)

    #     all_objectives_post = Objective.query.all()
        
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertEqual(len(all_objective_post) - len(all_objectives_pre), 1)

    def test_post_new_objective_fail(self):
        new_objective = {
            'objective_typo': 'Do better test driven development',
            'requirements': [{'description:': 'Implement one test'},
                             {'description': 'Implement two tests'}]
        }

        all_objectives_pre = Objective.query.all()

        res = self.client.post('/objectives', json = new_objective)
        data = json.loads(res.data)

        all_objectives_post = Objective.query.all()
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(len(all_objectives_post) - len(all_objectives_pre), 0)

    # fake access headers
    # def test_foo():
        # test_client = app.test_client()
        # access_token = create_access_token('testuser')
        # headers = {
            # 'Authorization': 'Bearer {}'.format(access_token)
        # }
        # response = test_client.get('/foo', headers=headers)
        # # Rest of test code here

    """
    One test for success behavior of each endpoint
    One test for error behavior of each endpoint
    At least two tests of RBAC for each role
    """


# Make tests conveniently executable
if __name__ == "__main__":
    unittest.main()