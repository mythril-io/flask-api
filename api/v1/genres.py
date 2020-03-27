import flask_praetorian
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError

from models import Genre
from .schemas import genre_schema, genres_schema
from . import api as api_v1

api = Namespace('genres', description='Genre operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_genre = api_v1.model('Genre', {
    'name': fields.String(required=True, description='Name'),
    'acronym': fields.String(required=False, description='Acronym'),
})

@api.route('/all')
class AllGenres(Resource):
    def get(self):
        """
        Get all Genres
        """
        genres = Genre.query.all()
        return genres_schema.dump(genres)

@api.route('/')
class Genres(Resource):
    def get(self):
        """
        List Genres
        """
        genres = Genre.query.all()
        return genres_schema.dump(genres)

    @flask_praetorian.roles_required('admin')
    @api.expect(a_genre)
    def post(self):
        """
        Add new Genre
        """
        req = api.payload
        
        # Validate 
        try:
            new_genre = genre_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }
            
        # Add Genre
        try:
            db.session.add(new_genre)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Genre'}, 500
        
        return genre_schema.dump(new_genre), 201

@api.route('/<int:id>')
class SingleGenre(Resource):
    def get(self, id):
        """
        Get Genre by id
        """
        genre = Genre.query.filter_by(id=id).first()
        if genre is None:
            return { 'message': 'Genre does not exist'}, 404

        return genre_schema.dump(genre)
    
    @flask_praetorian.roles_required('admin')
    @api.expect(a_genre)
    def put(self, id):
        """
        Update a Genre
        """
        req = api.payload
        
        # Fetch Genre
        genre = Genre.query.filter_by(id=id).first()
        if genre is None:
            return { 'message': 'Genre does not exist'}, 404

        # Validate        
        try:
            edit_genre = genre_schema.load(req)
        except ValidationError:
            return { 'error': err.messages }
        
        # Edit Genre
        genre.name = edit_genre.name

        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit Genre'}, 500

        return { 'message': 'Role updated successfully' }

    @flask_praetorian.roles_required('admin')
    def delete(self, id):
        """
        Delete a Genre by id
        """
        genre = Genre.query.filter_by(id=id).first()
        if genre is None:
            return { 'message': 'Genre does not exist'}, 404
            
        try:
            db.session.delete(genre)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Genre'}, 500
        
        return { 'message': 'Genre deleted successfully' }