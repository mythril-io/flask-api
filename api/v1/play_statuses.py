import flask_praetorian
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError

from models import PlayStatus
from .schemas import play_status_schema, play_statuses_schema
from . import api as api_v1

api = Namespace('playstatuses', description='Play Status operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_play_status = api_v1.model('PlayStatus', {
    'name': fields.String(required=True, description='Name'),
})

@api.route('/')
class PlayStatuses(Resource):
    def get(self):
        """
        List Play Statuses
        """
        statuses = PlayStatus.query.all()
        return play_statuses_schema.dump(statuses)

    @flask_praetorian.roles_required('admin')
    @api.expect(a_play_status)
    def post(self):
        """
        Add new Play Status
        """
        req = api.payload
        
        # Validate        
        try:
            new_play_status = play_status_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }       

        # Add Play Status
        try:
            db.session.add(new_play_status)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Play Status'}, 500
        
        return play_status_schema.dump(new_play_status), 201

@api.route('/<int:id>')
class SinglePlayStatus(Resource):
    def get(self, id):
        """
        Get Play Status by id
        """
        status = PlayStatus.query.filter_by(id=id).first()
        if status is None:
            return { 'message': 'Play Status does not exist'}, 404

        return play_status_schema.dump(status)
    
    @flask_praetorian.roles_required('admin')
    @api.expect(a_play_status)
    def put(self, id):
        """
        Update a Play Status
        """
        req = api.payload
        
        # Fetch Play Status
        status = PlayStatus.query.filter_by(id=id).first()
        if status is None:
            return { 'message': 'Play Status does not exist'}, 404

        # Validate        
        try:
            play_status_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }
        
        # Edit Play Status
        status.name = req.get('name')
        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit Play Status'}, 500

        return { 'message': 'Play Status updated successfully' }

    @flask_praetorian.roles_required('admin')
    def delete(self, id):
        """
        Delete a Play Status by id
        """
        status = PlayStatus.query.filter_by(id=id).first()
        if status is None:
            return { 'message': 'Play Status does not exist'}, 404
            
        try:
            db.session.delete(status)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Play Status'}, 500
        
        return { 'message': 'Play Status deleted successfully' }