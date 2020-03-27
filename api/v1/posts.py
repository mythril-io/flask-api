import flask_praetorian
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError
from datetime import datetime

from models import Post
from .schemas import post_schema, user_schema, post_post_schema, post_patch_schema
from . import api as api_v1

api = Namespace('posts', description='Post operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_post = api_v1.model('Post', {
    'body': fields.String(required=True, description='Body'),
})

@api.route('/')
class Posts(Resource):
    @flask_praetorian.auth_required
    @api.expect(a_post)
    def post(self):
        """
        Add new Post
        """
        req = api.payload

        # Set Authenticated User
        current_user = flask_praetorian.current_user()
        
        # Validate        
        try:
            new_post = post_post_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }     

        new_post.user_id = current_user.id

        # Add Post
        try:
            db.session.add(new_post)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Post'}, 500
        
        return post_schema.dump(new_post), 201

@api.route('/<int:id>')
class SinglePost(Resource):
    def get(self, id):
        """
        Get Post by id
        """
        post = Post.query.filter_by(id=id).first()
        if post is None:
            return { 'message': 'Post does not exist'}, 404

        return post_schema.dump(post)

    @flask_praetorian.auth_required
    @api.expect(a_post)
    def patch(self, id):
        """
        Update a Post
        """
        with db.session.no_autoflush:
            req = api.payload
            
            # Fetch Post
            post = Post.query.filter_by(id=id).first()

            if post is None:
                return { 'message': 'Post does not exist'}, 404

            # Check User permission
            current_user = flask_praetorian.current_user()
            if post.user_id != current_user.id:
                return { 'message': 'Unauthorized to edit Post'}, 401

            # Validate        
            try:
                edit_post = post_patch_schema.load(req)
            except ValidationError as err:
                return { 'error': err.messages }

            # Edit Post
            post.body = edit_post.body
            post.edit_count += 1

            try:
                db.session.commit()
            except Exception:
                return { 'message': 'Unable to edit Post'}, 500

            return { 'message': 'Post updated successfully' }

    @flask_praetorian.auth_required
    def delete(self, id):
        """
        Delete a Post by id
        """

        # Fetch Post
        post = Post.query.filter_by(id=id).first()
        if post is None:
            return { 'message': 'Post does not exist'}, 404

        # Check User permission
        current_user = flask_praetorian.current_user()
        if post.user_id != current_user.id:
            return { 'message': 'Unauthorized to delete Post'}, 401
            
        try:
            db.session.delete(post)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Post'}, 500
        
        return { 'message': 'Post deleted successfully' }