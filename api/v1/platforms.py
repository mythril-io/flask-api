import flask_praetorian
from flask import request
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError

from models import Platform
from .schemas import platform_schema, platforms_schema
from . import api as api_v1

api = Namespace('platforms', description='Platform operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_platform = api_v1.model('Platform', {
    'name': fields.String(required=True, description='Name'),
})

@api.route('/all')
class AllPlatforms(Resource):
    def get(self):
        """
        Get all Platforms
        """
        platforms = Platform.query.all()
        return platforms_schema.dump(platforms)

@api.route('/', defaults={ 'page': 1 }, methods=['GET'])
@api.route('/', methods=['POST'])
@api.route('/page/<int:page>', methods=['GET'])
class Platforms(Resource):
    def get(self, page):
        """
        List Platforms
        """
        page = page
        per_page = 8
        search = request.args.get('search') or ''

        platforms = Platform.query.filter(Platform.name.like('%' + search + '%')).order_by(Platform.name.asc()).paginate(page,per_page,error_out=False)
        response = {
            'items': platforms_schema.dump(platforms.items),
            'has_next': platforms.has_next,
            'has_prev': platforms.has_prev,
            'next_num': platforms.next_num,
            'prev_num': platforms.prev_num,
            'page': platforms.page,
            'per_page': platforms.per_page,
            'pages': platforms.pages,
            'total': platforms.total       
        }
        return response

    @flask_praetorian.roles_required('admin')
    @api.expect(a_platform)
    def post(self):
        """
        Add new Platform
        """
        req = api.payload
        
        # Validate        
        try:
            new_platform = platform_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }       

        # Add Platform
        try:
            db.session.add(new_platform)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Platform'}, 500
        
        return platform_schema.dump(new_platform), 201

@api.route('/<int:id>')
class SinglePlatform(Resource):
    def get(self, id):
        """
        Get Platform by id
        """
        platform = Platform.query.filter_by(id=id).first()
        if platform is None:
            return { 'message': 'Platform does not exist'}, 404

        return platform_schema.dump(platform)
    
    @flask_praetorian.roles_required('admin')
    @api.expect(a_platform)
    def put(self, id):
        """
        Update a Platform
        """
        req = api.payload
        
        # Fetch Platform
        platform = Platform.query.filter_by(id=id).first()
        if platform is None:
            return { 'message': 'Platform does not exist'}, 404

        # Validate        
        try:
            edit_platform = platform_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }

        # Edit Platform
        platform.name = edit_platform.name
        platform.acronym = edit_platform.acronym

        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit Platform'}, 500

        return { 'message': 'Platform updated successfully' }

    @flask_praetorian.roles_required('admin')
    def delete(self, id):
        """
        Delete a Platform by id
        """
        platform = Platform.query.filter_by(id=id).first()
        if platform is None:
            return { 'message': 'Platform does not exist'}, 404
            
        try:
            db.session.delete(platform)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Platform'}, 500
        
        return { 'message': 'Platform deleted successfully' }