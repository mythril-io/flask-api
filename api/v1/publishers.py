import flask_praetorian
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError

from models import Publisher
from .schemas import publisher_schema, publishers_schema
from . import api as api_v1

api = Namespace('publishers', description='Publisher operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_publisher = api_v1.model('Publisher', {
    'name': fields.String(required=True, description='Name'),
})


@api.route('/all')
class AllPublishers(Resource):
    def get(self):
        """
        Get all Publishers
        """
        publishers = Publisher.query.all()
        return publishers_schema.dump(publishers)

@api.route('/')
class Publishers(Resource):
    def get(self):
        """
        List Publishers
        """
        publishers = Publisher.query.all()
        return publishers_schema.dump(publishers)

    @flask_praetorian.roles_required('admin')
    @api.expect(a_publisher)
    def post(self):
        """
        Add new Publisher
        """
        req = api.payload
        
        # Validate        
        try:
            new_publisher = publisher_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }       

        # Add Publisher
        try:
            db.session.add(new_publisher)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Publisher'}, 500
        
        return publisher_schema.dump(new_publisher), 201

@api.route('/<int:id>')
class SinglePublisher(Resource):
    def get(self, id):
        """
        Get Publisher by id
        """
        publisher = Publisher.query.filter_by(id=id).first()
        if publisher is None:
            return { 'message': 'Publisher does not exist'}, 404

        return publisher_schema.dump(publisher)
    
    @flask_praetorian.roles_required('admin')
    @api.expect(a_publisher)
    def put(self, id):
        """
        Update a Publisher
        """
        req = api.payload
        
        # Fetch Publisher
        publisher = Publisher.query.filter_by(id=id).first()
        if publisher is None:
            return { 'message': 'Publisher does not exist'}, 404

        # Validate        
        try:
            edit_publisher = publisher_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }

        # Edit Publisher
        publisher.name = edit_publisher.name
        publisher.country = edit_publisher.country

        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit Publisher'}, 500

        return { 'message': 'Publisher updated successfully' }

    @flask_praetorian.roles_required('admin')
    def delete(self, id):
        """
        Delete a Publisher by id
        """
        publisher = Publisher.query.filter_by(id=id).first()
        if publisher is None:
            return { 'message': 'Publisher does not exist'}, 404
            
        try:
            db.session.delete(publisher)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Publisher'}, 500
        
        return { 'message': 'Publisher deleted successfully' }