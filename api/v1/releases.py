import flask_praetorian
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError, INCLUDE

from models import Release, Game
from .schemas import releases_schema, release_schema
from . import api as api_v1

api = Namespace('releases', description='Release operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_release = api_v1.model('Release', {
    'title': fields.String(required=True, description='Title'),
    'synopsis': fields.String(required=True, description='Synopsis'),
})

@api.route('/game/<int:id>')
class Releases(Resource):
    def get(self, id):
        """
        List Releases for specified game
        """
        releases = Release.query.filter_by(game_id=id).all()
        return releases_schema.dump(releases)

    @flask_praetorian.roles_required('admin')
    @api.expect(a_release)
    def post(self, id):
        """
        Add new Release for specified game
        """
        req = api.payload
        
        game = Game.query.filter_by(id=id).first()
        if game is None:
            return { 'message': 'Game does not exist'}, 404

        # Validate 
        try:
            new_release = release_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }

        # Append Release
        game.releases.append(new_release)   

        # Add Release
        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Release'}, 500
        
        return release_schema.dump(new_release), 201

@api.route('/<int:id>')
class SingleRelease(Resource):
    def get(self, id):
        """
        Get Release by id
        """
        release = Release.query.filter_by(id=id).first()
        if release is None:
            return { 'message': 'Release does not exist'}, 404

        return release_schema.dump(release)
    
    @flask_praetorian.roles_required('admin')
    @api.expect(a_release)
    def patch(self, id):
        """
        Update a Release
        """
        req = api.payload
        
        # Fetch Release
        release = Release.query.filter_by(id=id).first()
        if release is None:
            return { 'message': 'Release does not exist'}, 404

        # Validate        
        try:
            edit_release = release_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }
        
        # Edit Release
        release.platform = edit_release.platform
        release.publisher = edit_release.publisher
        release.codeveloper = edit_release.codeveloper
        release.region = edit_release.region
        release.date = edit_release.date
        release.date_type = edit_release.date_type
        release.alternate_title = edit_release.alternate_title

        try:
            db.session.expunge(edit_release)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit Release'}, 500

        return { 'message': 'Release updated successfully' }

    @flask_praetorian.roles_required('admin')
    def delete(self, id):
        """
        Delete a Release by id
        """
        release = Release.query.filter_by(id=id).first()
        if release is None:
            return { 'message': 'Release does not exist'}, 404
            
        try:
            db.session.delete(release)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Release'}, 500
        
        return { 'message': 'Release deleted successfully' }