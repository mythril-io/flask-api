import flask_praetorian
from flask import request
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError

from models import DateType
from .schemas import date_type_schema, date_types_schema
from . import api as api_v1

api = Namespace('datetypes', description='Date Type operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_date_type = api_v1.model('DateType', {
    'format': fields.String(required=True, description='Format'),
})

@api.route('/all')
class AllDateTypes(Resource):
    def get(self):
        """
        Get all Date Types
        """
        date_types = DateType.query.all()
        return date_types_schema.dump(date_types)

@api.route('/', defaults={ 'page': 1 }, methods=['GET'])
@api.route('/', methods=['POST'])
@api.route('/page/<int:page>', methods=['GET'])
class DateTypes(Resource):
    def get(self, page):
        """
        List Date Types
        """
        page = page
        per_page = 8
        search = request.args.get('search') or ''

        date_types = DateType.query.filter(DateType.name.like('%' + search + '%')).order_by(DateType.name.asc()).paginate(page,per_page,error_out=False)
        response = {
            'items': date_types_schema.dump(date_types.items),
            'has_next': date_types.has_next,
            'has_prev': date_types.has_prev,
            'next_num': date_types.next_num,
            'prev_num': date_types.prev_num,
            'page': date_types.page,
            'per_page': date_types.per_page,
            'pages': date_types.pages,
            'total': date_types.total       
        }
        return response

    @flask_praetorian.roles_required('admin')
    @api.expect(a_date_type)
    def post(self):
        """
        Add new Date Type
        """
        req = api.payload
        
        # Validate        
        try:
            new_date_type = date_type_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }       

        # Add Date Type
        try:
            db.session.add(new_date_type)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Date Type'}, 500
        
        return date_type_schema.dump(new_date_type), 201

@api.route('/<int:id>')
class SingleDateType(Resource):
    def get(self, id):
        """
        Get Date Type by id
        """
        date_type = DateType.query.filter_by(id=id).first()
        if date_type is None:
            return { 'message': 'Date Type does not exist'}, 404

        return date_type_schema.dump(date_type)
    
    @flask_praetorian.roles_required('admin')
    @api.expect(a_date_type)
    def put(self, id):
        """
        Update a Date Type
        """
        req = api.payload
        
        # Fetch Date Type
        date_type = DateType.query.filter_by(id=id).first()
        if date_type is None:
            return { 'message': 'Date Type does not exist'}, 404

        # Validate        
        try:
            edit_date_type = date_type_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }

        # Edit Date Type
        date_type.format = edit_date_type.format

        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit Date Type'}, 500

        return { 'message': 'Date Type updated successfully' }

    @flask_praetorian.roles_required('admin')
    def delete(self, id):
        """
        Delete a Date Type by id
        """
        date_type = DateType.query.filter_by(id=id).first()
        if date_type is None:
            return { 'message': 'Date Type does not exist'}, 404
            
        try:
            db.session.delete(date_type)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Date Type'}, 500
        
        return { 'message': 'Date Type deleted successfully' }