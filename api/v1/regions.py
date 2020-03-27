import flask_praetorian
from flask import request
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError

from models import Region
from .schemas import region_schema, regions_schema
from . import api as api_v1

api = Namespace('regions', description='Region operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_region = api_v1.model('Region', {
    'name': fields.String(required=True, description='Name'),
})

@api.route('/all')
class AllRegions(Resource):
    def get(self):
        """
        Get all Regions
        """
        regions = Region.query.all()
        return regions_schema.dump(regions)

@api.route('/', defaults={ 'page': 1 }, methods=['GET'])
@api.route('/', methods=['POST'])
@api.route('/page/<int:page>', methods=['GET'])
class Regions(Resource):
    def get(self, page):
        """
        List Regions
        """
        page = page
        per_page = 8
        search = request.args.get('search') or ''

        regions = Region.query.filter(Region.name.like('%' + search + '%')).order_by(Region.name.asc()).paginate(page,per_page,error_out=False)
        response = {
            'items': regions_schema.dump(regions.items),
            'has_next': regions.has_next,
            'has_prev': regions.has_prev,
            'next_num': regions.next_num,
            'prev_num': regions.prev_num,
            'page': regions.page,
            'per_page': regions.per_page,
            'pages': regions.pages,
            'total': regions.total       
        }
        return response

    @flask_praetorian.roles_required('admin')
    @api.expect(a_region)
    def post(self):
        """
        Add new Region
        """
        req = api.payload
        
        # Validate        
        try:
            new_region = region_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }       

        # Add Region
        try:
            db.session.add(new_region)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Region'}, 500
        
        return region_schema.dump(new_region), 201

@api.route('/<int:id>')
class SingleRegion(Resource):
    def get(self, id):
        """
        Get Region by id
        """
        region = Region.query.filter_by(id=id).first()
        if region is None:
            return { 'message': 'Region does not exist'}, 404

        return region_schema.dump(region)
    
    @flask_praetorian.roles_required('admin')
    @api.expect(a_region)
    def put(self, id):
        """
        Update a Region
        """
        req = api.payload
        
        # Fetch Region
        region = Region.query.filter_by(id=id).first()
        if region is None:
            return { 'message': 'Region does not exist'}, 404

        # Validate        
        try:
            edit_region = region_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }

        # Edit Region
        region.name = edit_region.name
        region.acronym = edit_region.acronym

        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit Region'}, 500

        return { 'message': 'Region updated successfully' }

    @flask_praetorian.roles_required('admin')
    def delete(self, id):
        """
        Delete a Region by id
        """
        region = Region.query.filter_by(id=id).first()
        if region is None:
            return { 'message': 'Region does not exist'}, 404
            
        try:
            db.session.delete(region)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Region'}, 500
        
        return { 'message': 'Region deleted successfully' }