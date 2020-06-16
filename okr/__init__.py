import sys
from flask import Flask, request, abort, jsonify, render_template
from models import setup_db, Person, Objective, Requirement
from auth.auth import AuthError, requires_auth

ITEMS_PER_PAGE = 5

def paginate_items(request, selection):
    """
    This function takes the request with a list of items,
    which are then paginated, and a list of max length
    ITEMS_PER_PAGE is returned
    """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE

    items = [item.format() for item in selection]
    current_items = items[start:end]

    return current_items

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)

    @app.route('/persons')
    @requires_auth('get:persons')
    def retrieve_persons(payload):
        """
        GET /persons endpoint returns a list of persons
        working at the company.
        Requires basic permissions
        """
        selection = Person.query.order_by(Person.id).all()
        current_persons = paginate_items(request, selection)

        if len(current_persons) == 0:
            abort(404)
        
        return jsonify({
            'success': True,
            'persons': current_persons
        })

    @app.route('/objectives')
    @requires_auth('get:objectives')
    def retrieve_objectives(payload):
        """
        GET /objectives endpoint returns a list of all objectives
        from all persons at the company.
        Requires basic permissions
        """
        selection = Objective.query.order_by(Objective.id).all()
        current_objectives = paginate_items(request, selection)

        if len(current_objectives) == 0:
            abort(404)
        
        return jsonify({
            'success': True,
            'objectives': current_objectives
        })

    @app.route('/objectives/<int:objective_id>/requirements')
    @requires_auth('get:requirements')
    def retrieve_requirements(payload, objective_id):
        """
        GET /objectives/<id>/requirements endpoint returns a list of all
        requirements of a specific objective at the company.
        Requires basic permissions
        """
        selection = Requirement.query.filter(Requirement.objective == objective_id).order_by(Requirement.id).all()
        all_requirements = [item.format() for item in selection]

        if len(all_requirements) == 0:
            abort(404)
        
        return jsonify({
            'success': True,
            'requirements': all_requirements
        })

    @app.route('/objectives/<int:objective_id>', methods =['DELETE'])
    @requires_auth('delete:objectives')
    def delete_objective(payload, objective_id):
        """
        DELETE /objectives/<id> endpoint deletes a specific
        objective and all requirements part of it
        Requires more than basic permissions
        """
        objective = Objective.query.filter(Objective.id == objective_id).one_or_none()

        if objective is None:
            abort(404)

        deleted_id = objective.id
        objective.delete()

        return jsonify({
            'success': True,
            'deleted_id': deleted_id
        })

    @app.route('/requirements/<int:requirement_id>', methods =['DELETE'])
    @requires_auth('delete:requirements')
    def delete_requirement(payload, requirement_id):
        """
        DELETE /requirements/<id> endpoint deletes a specific
        requirement
        Requires more than basic permissions
        """
        requirement = Requirement.query.filter(Requirement.id == requirement_id).one_or_none()

        if requirement is None:
            abort(404)

        deleted_id = requirement.id
        requirement.delete()

        return jsonify({
            'success': True,
            'deleted_id': deleted_id
        })

    @app.route('/requirements/<int:requirement_id>', methods = ['PATCH'])
    @requires_auth('patch:requirements')
    def update_requirement(payload, requirement_id):
        """
        PATCH /requirements/<id> endpoint updates a specific
        requirement's status
        Requires basic permissions
        """
        try:
            body = request.get_json()

            assert requirement_id == body.get('requirement_id', None)

            requirement = Requirement.query.filter(Requirement.id == requirement_id).one_or_none()

            if requirement is None:
                abort(404)
            
            assert requirement.objective == body.get('objective_id', None)

            previous_status = requirement.is_met
            requirement.is_met = body.get('is_met', None)
            requirement.update()

            if previous_status != requirement.is_met:
                updated = True
            else:
                updated = False


            return jsonify({
                'success': True,
                'previous_status': previous_status,
                'is_met': requirement.is_met,
                'changed': updated
            })
        except:
            abort(422)


    @app.route('/objectives/<int:objective_id>/requirements', methods = ['POST'])
    @requires_auth('post:requirements')
    def new_requirement(payload, objective_id):
        """
        POST /objectives/<id>/requirements endpoint creates a specific
        new requirement to one objective
        Requires more than basic permissions
        """
        try:
            body = request.get_json()

            objective = Objective.query.filter(Objective.id == objective_id).one_or_none()

            if objective is None:
                abort(404)
            
            requirement = Requirement(body.get('description'), objective.id)
            requirement.insert()

            return jsonify({
                'success': True,
                'objective_id': objective_id,
                'new_requirement_id': requirement.id,
            })
        except:
            abort(422)

    @app.route('/objectives', methods = ['POST'])
    @requires_auth('post:objectives')
    def new_objective(payload):
        """
        POST /objectives endpoint creates a specific
        new objective with one single requirement
        Requires more than basic permissions
        """
        try:
            body = request.get_json()

            objective = Objective(body.get('objective'),
                                body.get('person'))
            objective.insert()

            # for item in body.get('requirements'):
            #     requirement = Requirement(item.get('description'),
            #                               objective.id)
            #     requirement.insert()

            requirement = Requirement(body.get('requirements'),
                                    objective.id)
            requirement.insert()

            return jsonify({'success': True,
                            'objective_id': objective.id,
                            'n_requirements': len(body.get('requirements'))})
        except:
            abort(422)


    @app.errorhandler(404)
    def resource_not_found(error):
        '''
        Example error handling for resource not found
        '''
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404
    

    @app.errorhandler(422)
    def request_body_malformed(error):
        '''
        Example error handling for malformed request body
        '''
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'request body malformed'
        }), 422


    @app.errorhandler(AuthError)
    def handle_auth_error(error):
        '''
        Example error handling for authorization errors
        '''
        return jsonify({'success': False,
                        'error': error.status_code,
                        'message': error.error}), error.status_code

    return app