import flask_praetorian
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError
from datetime import datetime

from models import Discussion
from .schemas import discussion_schema, discussions_schema, user_schema, discussion_post_schema, discussion_patch_schema
from . import api as api_v1

api = Namespace('discussions', description='Discussion operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_discussion = api_v1.model('Discussion', {
    'title': fields.String(required=True, description='Title'),
    'body': fields.String(required=True, description='Body'),
})

@api.route('/')
class Discussions(Resource):
    def get(self):
        """
        List Discussions
        """
        discussions = Discussion.query.all()
        return discussions_schema.dump(discussions)

    @flask_praetorian.auth_required
    @api.expect(a_discussion)
    def post(self):
        """
        Add new Discussion
        """
        req = api.payload

        # Set Authenticated User
        current_user = flask_praetorian.current_user()
        
        # Validate        
        try:
            new_discussion = discussion_post_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }     

        new_discussion.slug = 'slug2'
        new_discussion.user_id = current_user.id

        # Add Discussion
        try:
            db.session.add(new_discussion)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Discussion'}, 500
        
        return discussion_schema.dump(new_discussion), 201

@api.route('/<int:id>')
class SingleDiscussion(Resource):
    def get(self, id):
        """
        Get Discussion by id
        """
        discussion = Discussion.query.filter_by(id=id).first()
        if discussion is None:
            return { 'message': 'Discussion does not exist'}, 404

        # Update Discussion view count
        discussion.view_count += 1

        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to update Discussion view count'}, 500

        return discussion_schema.dump(discussion)

    @flask_praetorian.auth_required
    @api.expect(a_discussion)
    def patch(self, id):
        """
        Update a Discussion
        """
        with db.session.no_autoflush:
            req = api.payload
            
            # Fetch Discussion
            discussion = Discussion.query.filter_by(id=id).first()

            if discussion is None:
                return { 'message': 'Discussion does not exist'}, 404

            # Check User permission
            current_user = flask_praetorian.current_user()
            if discussion.user_id != current_user.id:
                return { 'message': 'Unauthorized to edit Discussion'}, 401

            # Validate        
            try:
                edit_discussion = discussion_patch_schema.load(req)
            except ValidationError as err:
                return { 'error': err.messages }

            # Edit Discussion
            discussion.body = edit_discussion.body
            discussion.edited_at = datetime.now()
            discussion.edit_count += 1

            try:
                db.session.commit()
            except Exception:
                return { 'message': 'Unable to edit Discussion'}, 500

            return { 'message': 'Discussion updated successfully' }

    @flask_praetorian.auth_required
    def delete(self, id):
        """
        Delete a Discussion by id
        """

        # Fetch Discussion
        discussion = Discussion.query.filter_by(id=id).first()
        if discussion is None:
            return { 'message': 'Discussion does not exist'}, 404

        # Check User permission
        current_user = flask_praetorian.current_user()
        if discussion.user_id != current_user.id:
            return { 'message': 'Unauthorized to delete Discussion'}, 401
            
        try:
            db.session.delete(discussion)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Discussion'}, 500
        
        return { 'message': 'Discussion deleted successfully' }