import flask_praetorian
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError

from models import Tag
from .schemas import tag_schema, tags_schema
from . import api as api_v1

api = Namespace('tags', description='Forum Tag operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_tag = api_v1.model('Tag', {
    'name': fields.String(required=True, description='Name'),
})

@api.route('/')
class Tags(Resource):
    def get(self):
        """
        List Tags
        """
        tags = Tag.query.all()
        return tags_schema.dump(tags)

    @flask_praetorian.roles_required('admin')
    @api.expect(a_tag)
    def post(self):
        """
        Add new Tag
        """
        req = api.payload
        
        # Validate        
        try:
            new_tag = tag_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }       

        # Add Tag
        try:
            db.session.add(new_tag)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Tag'}, 500
        
        return tag_schema.dump(new_tag), 201

@api.route('/<int:id>')
class SingleTag(Resource):
    def get(self, id):
        """
        Get Tag by id
        """
        tag = Tag.query.filter_by(id=id).first()
        if tag is None:
            return { 'message': 'Tag does not exist'}, 404

        return tag_schema.dump(tag)
    
    @flask_praetorian.roles_required('admin')
    @api.expect(a_tag)
    def put(self, id):
        """
        Update a Tag
        """
        req = api.payload
        
        # Fetch Tag
        tag = Tag.query.filter_by(id=id).first()
        if tag is None:
            return { 'message': 'Tag does not exist'}, 404

        # Validate        
        try:
            edit_tag = tag_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }
        
        # Edit Tag
        tag.name = edit_tag.name
        tag.slug = edit_tag.slug
        tag.colour = edit_tag.colour
        tag.order = edit_tag.order
        
        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit Tag'}, 500

        return { 'message': 'Tag updated successfully' }

    @flask_praetorian.roles_required('admin')
    def delete(self, id):
        """
        Delete a Tag by id
        """
        tag = Tag.query.filter_by(id=id).first()
        if tag is None:
            return { 'message': 'Tag does not exist'}, 404
            
        try:
            db.session.delete(tag)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Tag'}, 500
        
        return { 'message': 'Tag deleted successfully' }