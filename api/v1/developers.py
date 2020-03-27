import flask_praetorian
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError

from models import Developer
from .schemas import developer_schema, developers_schema
from . import api as api_v1

api = Namespace('developers', description='Developer operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_developer = api_v1.model('Developer', {
    'name': fields.String(required=True, description='Name'),
})

@api.route('/all')
class AllDevelopers(Resource):
    def get(self):
        """
        List Developers
        """
        developers = Developer.query.all()
        return developers_schema.dump(developers)

@api.route('/')
class Developers(Resource):
    def get(self):
        """
        List Developers
        """
        developers = Developer.query.all()
        return developers_schema.dump(developers)

    @flask_praetorian.roles_required('admin')
    @api.expect(a_developer)
    def post(self):
        """
        Add new Developer
        """
        req = api.payload
        
        # Validate        
        try:
            new_developer = developer_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }       

        # Add Developer
        try:
            db.session.add(new_developer)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Developer'}, 500
        
        return developer_schema.dump(new_developer), 201

@api.route('/<int:id>')
class SingleDeveloper(Resource):
    def get(self, id):
        """
        Get Developer by id
        """
        developer = Developer.query.filter_by(id=id).first()
        if developer is None:
            return { 'message': 'Developer does not exist'}, 404

        return developer_schema.dump(developer)
    
    @flask_praetorian.roles_required('admin')
    @api.expect(a_developer)
    def put(self, id):
        """
        Update a Developer
        """
        req = api.payload
        
        # Fetch Developer
        developer = Developer.query.filter_by(id=id).first()
        if developer is None:
            return { 'message': 'Developer does not exist'}, 404

        # Validate        
        try:
            edit_developer = developer_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }

        # Edit Developer
        developer.name = edit_developer.name
        developer.country = edit_developer.country

        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit Developer'}, 500

        return { 'message': 'Developer updated successfully' }

    @flask_praetorian.roles_required('admin')
    def delete(self, id):
        """
        Delete a Developer by id
        """
        developer = Developer.query.filter_by(id=id).first()
        if developer is None:
            return { 'message': 'Developer does not exist'}, 404
            
        try:
            db.session.delete(developer)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Developer'}, 500
        
        return { 'message': 'Developer deleted successfully' }