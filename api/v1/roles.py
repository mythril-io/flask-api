import flask_praetorian
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError

from models import Role
from .schemas import role_schema, roles_schema
from . import api as api_v1

api = Namespace('roles', description='Role operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_role = api_v1.model('Role', {
    'name': fields.String(required=True, description='Name'),
})

@api.route('/')
class Roles(Resource):
    def get(self):
        """
        List Roles
        """
        roles = Role.query.all()
        return roles_schema.dump(roles)

    @flask_praetorian.roles_required('admin')
    @api.expect(a_role)
    def post(self):
        """
        Add new Role
        """
        req = api.payload
        
        # Validate        
        try:
            new_role = role_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }       

        # Add Role
        try:
            db.session.add(new_role)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Role'}, 500
        
        return role_schema.dump(new_role), 201

@api.route('/<int:id>')
class SingleRole(Resource):
    def get(self, id):
        """
        Get Role by id
        """
        role = Role.query.filter_by(id=id).first()
        if role is None:
            return { 'message': 'Role does not exist'}, 404

        return role_schema.dump(role)
    
    @flask_praetorian.roles_required('admin')
    @api.expect(a_role)
    def put(self, id):
        """
        Update a Role
        """
        req = api.payload
        
        # Fetch Role
        role = Role.query.filter_by(id=id).first()
        if role is None:
            return { 'message': 'Role does not exist'}, 404

        # Validate        
        try:
            edit_role = role_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }
        
        # Edit Role
        role.name = edit_role.name
        
        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit Role'}, 500

        return { 'message': 'Role updated successfully' }

    @flask_praetorian.roles_required('admin')
    def delete(self, id):
        """
        Delete a Role by id
        """
        role = Role.query.filter_by(id=id).first()
        if role is None:
            return { 'message': 'Role does not exist'}, 404
            
        try:
            db.session.delete(role)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Role'}, 500
        
        return { 'message': 'Role deleted successfully' }