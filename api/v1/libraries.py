import flask_praetorian
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError
from sqlalchemy import and_

from models import LibraryEntry
from .schemas import library_entry_schema, library_entries_schema, library_entry_post_schema, library_entry_patch_schema, user_schema
from . import api as api_v1

api = Namespace('libraries', description='Library operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_library_entry = api_v1.model('LibraryEntry', {
    'name': fields.String(required=True, description='Name'),
})

@api.route('/')
class Libraries(Resource):
    def get(self):
        """
        List Libraries grouped by User
        """
        user_libraries = LibraryEntry.query.all()
        return library_entries_schema.dump(user_libraries)

    @flask_praetorian.auth_required
    @api.expect(a_library_entry)
    def post(self):
        """
        Add a new Library Entry
        """
        req = api.payload

        # Set Authenticated User
        current_user = flask_praetorian.current_user()
        req['user'] = user_schema.dump(current_user)

        # Validate        
        try:
            new_library_entry = library_entry_post_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }

        # Add Library
        try:
            db.session.add(new_library_entry)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Library Entry'}, 500
        
        return library_entry_schema.dump(new_library_entry), 201

@api.route('/<int:id>')
class SingleLibraryEntry(Resource):
    def get(self, id):
        """
        Get Library Entry by id
        """
        library_entry = LibraryEntry.query.filter_by(id=id).first()
        if library_entry is None:
            return { 'message': 'Library Entry does not exist'}, 404

        return library_entry_schema.dump(library_entry)
    
    @flask_praetorian.auth_required
    @api.expect(a_library_entry)
    def patch(self, id):
        """
        Update a Library Entry
        """
        with db.session.no_autoflush:
            req = api.payload
            
            # Fetch Library Entry
            library_entry = LibraryEntry.query.filter_by(id=id).first()
            if library_entry is None:
                return { 'message': 'Library Entry does not exist'}, 404

            # Check User permission
            current_user = flask_praetorian.current_user()
            if library_entry.user_id != current_user.id:
                return { 'message': 'Unauthorized to edit Library Entry'}, 401

            # Validate        
            try:
                edit_entry = library_entry_patch_schema.load(req)
            except ValidationError as err:
                return { 'error': err.messages }

            # Edit Library Entry
            library_entry.digital = edit_entry.digital
            library_entry.hours = edit_entry.hours
            library_entry.own = edit_entry.own
            library_entry.notes = edit_entry.notes
            library_entry.score = edit_entry.score
            library_entry.play_status = edit_entry.play_status

            try:
                db.session.commit()
            except Exception:
                return { 'message': 'Unable to edit Library Entry'}, 500

            return { 'message': 'Library Entry updated successfully' }

    @flask_praetorian.auth_required
    def delete(self, id):
        """
        Delete a Library Entry by id
        """

        # Fetch Library Entry
        library_entry = LibraryEntry.query.filter_by(id=id).first()
        if library_entry is None:
            return { 'message': 'Library Entry does not exist'}, 404

        # Check User permission
        current_user = flask_praetorian.current_user()
        if library_entry.user_id != current_user.id:
            return { 'message': 'Unauthorized to delete Library Entry'}, 401
            
        try:
            db.session.delete(library_entry)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Library Entry'}, 500
        
        return { 'message': 'Library Entry deleted successfully' }

@api.route('/recent')
class RecentLibraryEntries(Resource):
    def get(self):
        """
        Get Recent Library Entries
        """
        recent_library_entries = LibraryEntry.query.order_by(LibraryEntry.created_at.desc()).limit(8).all()

        return library_entries_schema.dump(recent_library_entries)

@api.route('/user/<int:id>')
class UserLibrary(Resource):
    def get(self, id):
        """
        Get Library Entries by User id
        """
        user_library = LibraryEntry.query.filter_by(user_id=id).all()
        if user_library is None:
            return { 'message': 'User has no Library'}, 404

        return library_entries_schema.dump(user_library)

@api.route('/user/<int:id>/status/<int:play_id>', defaults={ 'page': 1 }, methods=['GET'])
@api.route('/user/<int:id>/status/<int:play_id>/page/<int:page>', methods=['GET'])
class UserStatusLibrary(Resource):
    def get(self, id, play_id, page):
        """
        Get Library Entries by User id and Play Status
        """
        page = page
        per_page = 10

        user_library = LibraryEntry.query.filter(LibraryEntry.user_id==id, LibraryEntry.play_status_id==play_id).paginate(page,per_page,error_out=False)
        if user_library.items is None:
            return { 'message': 'User has no Library'}, 404

        response = {
            'items': library_entries_schema.dump(user_library.items),
            'has_next': user_library.has_next,
            'has_prev': user_library.has_prev,
            'next_num': user_library.next_num,
            'prev_num': user_library.prev_num,
            'page': user_library.page,
            'per_page': user_library.per_page,
            'pages': user_library.pages,
            'total': user_library.total       
        }
        return response

@api.route('/game/<int:id>')
class GameUserLibrary(Resource):
    @flask_praetorian.auth_required
    def get(self, id):
        """
        Get Library Entries by User id and Game id
        """
        current_user = flask_praetorian.current_user()
        
        user_library = LibraryEntry.query.filter(and_(
                LibraryEntry.user_id==current_user.id, 
                LibraryEntry.game_id==id
            )).all()
        if user_library is None:
            return { 'message': 'User has no Library Entries for specified Game'}, 404

        return library_entries_schema.dump(user_library)


@api.route('/game/<int:id>/recent')
class RecentGameLibrary(Resource):
    def get(self, id):
        """
        Get recent Library Entries by Game id
        """
        
        recent_library = LibraryEntry.query.filter(LibraryEntry.game_id==id).order_by(LibraryEntry.created_at.asc()).limit(4).all()
        if recent_library is None:
            return { 'message': 'No Library Entries for specified Game'}, 404

        return library_entries_schema.dump(recent_library)