import flask_praetorian
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError

from models import Favourite
from .schemas import favourite_schema, favourites_schema, user_schema, favourite_post_schema, favourite_patch_schema
from . import api as api_v1

api = Namespace('favourites', description='Favourite operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_favourite = api_v1.model('Favourite', {
})

@api.route('/')
class Favourites(Resource):
    def get(self):
        """
        List Favourites
        """
        favourites = Favourite.query.all()
        return favourites_schema.dump(favourites)

    @flask_praetorian.auth_required
    @api.expect(a_favourite)
    def post(self):
        """
        Add new Favourite
        """
        req = api.payload

        # Set Authenticated User
        current_user = flask_praetorian.current_user()
        req['user'] = user_schema.dump(current_user)
        
        # Validate        
        try:
            new_favourite = favourite_post_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }       

        # Add Favourite
        try:
            db.session.add(new_favourite)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Favourite'}, 500

        return favourite_schema.dump(new_favourite), 201

@api.route('/<int:id>')
class SingleFavourite(Resource):
    def get(self, id):
        """
        Get Favourite by id
        """
        favourite = Favourite.query.filter_by(id=id).first()
        if favourite is None:
            return { 'message': 'Favourite does not exist'}, 404

        return favourite_schema.dump(favourite)

    @flask_praetorian.auth_required
    def patch(self, id):
        """
        Patch a Favourite by id
        """
        req = api.payload

        favourite = Favourite.query.filter_by(id=id).first()
        if favourite is None:
            return { 'message': 'Favourite does not exist'}, 404

        # Check User permission
        current_user = flask_praetorian.current_user()
        if favourite.user_id != current_user.id:
            return { 'message': 'Unauthorized to edit Favourite'}, 401
            
        # Validate        
        try:
            edit_favourite = favourite_patch_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }

        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit Favourite'}, 500

        return { 'message': 'Favourite updated successfully' }

    @flask_praetorian.auth_required
    def delete(self, id):
        """
        Delete a Favourite by id
        """

        # Fetch Favourite
        favourite = Favourite.query.filter_by(id=id).first()
        if favourite is None:
            return { 'message': 'Favourite does not exist'}, 404

        # Check User permission
        current_user = flask_praetorian.current_user()
        if favourite.user_id != current_user.id:
            return { 'message': 'Unauthorized to delete Favourite'}, 401
            
        try:
            db.session.delete(favourite)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Favourite'}, 500
        
        return { 'message': 'Favourite deleted successfully' }

@api.route('/user/<int:id>')
class UserFavourites(Resource):
    def get(self, id):
        """
        Get Favourites by User id
        """
        user_favourites = Favourite.query.filter_by(user_id=id).all()
        if user_favourites is None:
            return { 'message': 'User has no Favourites'}, 404

        return favourites_schema.dump(user_favourites)

@api.route('/game/<int:id>')
class UserGameFavourite(Resource):
    @flask_praetorian.auth_required
    def get(self, id):
        """
        List Favourites
        """
        current_user = flask_praetorian.current_user()
        # return user_schema.dump(current_user)
        favourite = Favourite.query.filter_by(user_id=current_user.id, game_id=id).first()
        if favourite is None:
            return None, 404

        return favourite_schema.dump(favourite)