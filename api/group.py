import jwt 
from sqlite3 import IntegrityError
from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource  # used for REST API building
from datetime import datetime
from __init__ import app, db
from api.jwt_authorize import token_required
from model.group import Group
from model.user import User
from model.section import Section

"""
This Blueprint object is used to define APIs for the Group model.
- Blueprint is used to modularize application files.
- This Blueprint is registered to the Flask app in main.py.
"""
group_api = Blueprint('group_api', __name__, url_prefix='/api')

"""
The Api object is connected to the Blueprint object to define the API endpoints.
- The API object is used to add resources to the API.
- The objects added are mapped to code that contains the actions for the API.
- For more information, refer to the API docs: https://flask-restful.readthedocs.io/en/latest/api.html
"""
api = Api(group_api)

class GroupAPI:
    """
    Define the API CRUD endpoints for the Group model.
    There are four operations that correspond to common HTTP methods:
    - post: create a new group
    - get: read groups
    - put: update a group
    - delete: delete a group
    """
    class _CRUD(Resource):
        @token_required()
        def post(self):
            """
            Create a new group.
            """
            # Obtain the current user from the token required setting in the global context
            current_user = g.current_user
            # Obtain the request data sent by the RESTful client API
            data = request.get_json()
            # Create a new group object using the data from the request
            group = Group(data['name'], data['section_id'], data.get('moderator_id', current_user.id))
            # Save the group object using the Object Relational Mapper (ORM) method defined in the model
            group.create()
            # Return response to the client in JSON format, converting Python dictionaries to JSON format
            return jsonify(group.read())

        @token_required()
        def get(self):
            """
            Retrieve a single group by ID.
            """
            # Obtain and validate the request data sent by the RESTful client API
            data = request.get_json()
            if data is None:
                return {'message': 'Group data not found'}, 400
            if 'id' not in data:
                return {'message': 'Group ID not found'}, 400
            # Find the group to read
            group = Group.query.get(data['id'])
            if group is None:
                return {'message': 'Group not found'}, 404
            # Convert Python object to JSON format 
            json_ready = group.read()
            # Return a JSON restful response to the client
            return jsonify(json_ready)

        @token_required()
        def put(self):
            """
            Update a group.
            """
            # Obtain the current user from the token required setting in the global context
            current_user = g.current_user
            # Obtain the request data sent by the RESTful client API
            data = request.get_json()
            # Find the group to update
            group = Group.query.get(data['id'])
            if group is None:
                return {'message': 'Group not found'}, 404
            # Update the group object using the data from the request
            group._name = data['name']
            group._section_id = data['section_id']
            group._moderator_id = data.get('moderator_id', current_user.id)
            # Save the group object using the Object Relational Mapper (ORM) method defined in the model
            group.update()
            # Return response to the client in JSON format, converting Python dictionaries to JSON format
            return jsonify(group.read())

        @token_required()
        def delete(self):
            """
            Delete a group.
            """
            # Obtain the request data sent by the RESTful client API
            data = request.get_json()
            # Find the group to delete
            group = Group.query.get(data['id'])
            if group is None:
                return {'message': 'Group not found'}, 404
            # Delete the group object using the Object Relational Mapper (ORM) method defined in the model
            group.delete()
            # Return response to the client in JSON format, converting Python dictionaries to JSON format
            return jsonify({'message': 'Group deleted'})

    class _BULK_CRUD(Resource):
        def post(self):
            """
            Handle bulk group creation by sending POST requests to the single group endpoint.
            """
            groups = request.get_json()

            if not isinstance(groups, list):
                return {'message': 'Expected a list of group data'}, 400

            results = {'errors': [], 'success_count': 0, 'error_count': 0}

            with current_app.test_client() as client:
                for group in groups:
                    # Simulate a POST request to the single group creation endpoint
                    response = client.post('/api/group', json=group)

                    if response.status_code == 200:
                        results['success_count'] += 1
                    else:
                        results['errors'].append(response.get_json())
                        results['error_count'] += 1

            # Return the results of the bulk creation process
            return jsonify(results)
        
        def get(self):
            """
            Retrieve all groups.
            """
            # Find all the groups
            groups = Group.query.all()
            # Prepare a JSON list of all the groups, using list comprehension
            json_ready = []
            for group in groups:
                group_data = group.read()
                json_ready.append(group_data)
            # Return a JSON list, converting Python dictionaries to JSON format
            return jsonify(json_ready)

    class _MODERATOR(Resource):
        @token_required()
        def post(self):
            """
            Add a moderator to a group.
            """
            # Obtain the request data sent by the RESTful client API
            data = request.get_json()
            # Find the group to update
            group = Group.query.get(data['group_id'])
            if group is None:
                return {'message': 'Group not found'}, 404
            # Find the user to add as a moderator
            user = User.query.get(data['user_id'])
            if user is None:
                return {'message': 'User not found'}, 404
            # Add the user as a moderator
            group.moderators.append(user)
            # Save the group object using the Object Relational Mapper (ORM) method defined in the model
            group.update()
            # Return response to the client in JSON format, converting Python dictionaries to JSON format
            return jsonify(group.read())

        @token_required()
        def delete(self):
            """
            Remove a moderator from a group.
            """
            # Obtain the request data sent by the RESTful client API
            data = request.get_json()
            # Find the group to update
            group = Group.query.get(data['group_id'])
            if group is None:
                return {'message': 'Group not found'}, 404
            # Find the user to remove as a moderator
            user = User.query.get(data['user_id'])
            if user is None:
                return {'message': 'User not found'}, 404
            # Remove the user as a moderator
            group.moderators.remove(user)
            # Save the group object using the Object Relational Mapper (ORM) method defined in the model
            group.update()
            # Return response to the client in JSON format, converting Python dictionaries to JSON format
            return jsonify(group.read())

    class _BULK_FILTER(Resource):
        @token_required()
        def post(self):
            """
            Retrieve all groups under a section by section name.
            """
            # Obtain and validate the request data sent by the RESTful client API
            data = request.get_json()
            if data is None:
                return {'message': 'Section data not found'}, 400
            if 'section_name' not in data:
                return {'message': 'Section name not found'}, 400
            
            # Find the section by name
            section = Section.query.filter_by(_name=data['section_name']).first()
            if section is None:
                return {'message': 'Section not found'}, 404
            
            # Find all groups under the section
            groups = Group.query.filter_by(_section_id=section.id).all()
            # Prepare a JSON list of all the groups, using list comprehension
            json_ready = [group.read() for group in groups]
            # Return a JSON list, converting Python dictionaries to JSON format
            return jsonify(json_ready)

    class _FILTER(Resource):
        @token_required()
        def post(self):
            """
            Retrieve a single group by group name.
            """
            # Obtain and validate the request data sent by the RESTful client API
            data = request.get_json()
            if data is None:
                return {'message': 'Group data not found'}, 400
            if 'group_name' not in data:
                return {'message': 'Group name not found'}, 400
            
            # Find the group by name
            group = Group.query.filter_by(_name=data['group_name']).first()
            if group is None:
                return {'message': 'Group not found'}, 404
            
            # Convert Python object to JSON format 
            json_ready = group.read()
            # Return a JSON restful response to the client
            return jsonify(json_ready)

    """
    Map the _CRUD, _BULK_CRUD, _BULK_FILTER, and _FILTER classes to the API endpoints for /group, /groups, /groups/filter, and /group/filter.
    - The API resource class inherits from flask_restful.Resource.
    - The _CRUD class defines the HTTP methods for the API.
    - The _BULK_CRUD class defines the bulk operations for the API.
    - The _BULK_FILTER class defines the endpoints for filtering groups by section name.
    - The _FILTER class defines the endpoints for filtering a specific group by group name.
    """
    api.add_resource(_CRUD, '/group')
    api.add_resource(_BULK_CRUD, '/groups')
    api.add_resource(_BULK_FILTER, '/groups/filter')
    api.add_resource(_FILTER, '/group/filter')

def initGroups():
    with app.app_context():
        db.create_all()
        bookworm_section = Section.query.filter_by(_name='Bookworms').first()
        groups += [
            Group(name='Classics', section_id=bookworm_section.id, moderators=[User.query.get(1)]),
            Group(name='Fantasy', section_id=bookworm_section.id, moderators=[User.query.get(1)]),
            Group(name='Nonfiction', section_id=bookworm_section.id, moderators=[User.query.get(1)]),
            Group(name='Historical Fiction', section_id=bookworm_section.id, moderators=[User.query.get(1)]),
            Group(name='Suspense/Thriller', section_id=bookworm_section.id, moderators=[User.query.get(1)]),
            Group(name='Romance', section_id=bookworm_section.id, moderators=[User.query.get(1)]),
            Group(name='Dystopian', section_id=bookworm_section.id, moderators=[User.query.get(1)]),
            Group(name='Mystery', section_id=bookworm_section.id, moderators=[User.query.get(1)]),
        ]
        for group in groups:
            try:
                db.session.add(group)
                db.session.commit()
                print(f"Record created: {repr(group)}")
            except IntegrityError:
                db.session.rollback()
                print(f"Records exist, duplicate email, or error: {group._name}")
