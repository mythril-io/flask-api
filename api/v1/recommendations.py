import flask_praetorian
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError

from models import Recommendation
from .schemas import recommendation_schema, recommendations_schema, user_schema, recommendation_post_schema, recommendation_patch_schema
from . import api as api_v1

api = Namespace('recommendations', description='Recommendation operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_recommendation = api_v1.model('Recommendation', {
    'content': fields.String(required=True, description='Content')
})

@api.route('/all')
class AllRecommendations(Resource):
    def get(self):
        """
        Get all Recommendations
        """
        recommendations = Recommendation.query.all()
        return recommendations_schema.dump(recommendations)

@api.route('/', defaults={ 'page': 1 }, methods=['GET'])
@api.route('/', methods=['POST'])
@api.route('/page/<int:page>', methods=['GET'])
class Recommendations(Resource):
    def get(self, page):
        """
        List Recommendations
        """
        page = page
        per_page = 8

        recommendations = Recommendation.query.order_by(Recommendation.created_at.desc()).paginate(page,per_page,error_out=False)
        response = {
            'items': recommendations_schema.dump(recommendations.items),
            'has_next': recommendations.has_next,
            'has_prev': recommendations.has_prev,
            'next_num': recommendations.next_num,
            'prev_num': recommendations.prev_num,
            'page': recommendations.page,
            'per_page': recommendations.per_page,
            'pages': recommendations.pages,
            'total': recommendations.total       
        }
        return response

    @flask_praetorian.auth_required
    @api.expect(a_recommendation)
    def post(self):
        """
        Add new Recommendation
        """
        req = api.payload

        # Set Authenticated User
        current_user = flask_praetorian.current_user()
        req['user'] = user_schema.dump(current_user)
        
        # Validate        
        try:
            new_recommendation = recommendation_post_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }       

        # Add Recommendation
        try:
            db.session.add(new_recommendation)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Recommendation'}, 500
        
        return recommendation_schema.dump(new_recommendation), 201

@api.route('/<int:id>')
class SingleRecommendation(Resource):
    def get(self, id):
        """
        Get Recommendation by id
        """
        recommendation = Recommendation.query.filter_by(id=id).first()
        if recommendation is None:
            return { 'message': 'Recommendation does not exist'}, 404

        return recommendation_schema.dump(recommendation)

    @flask_praetorian.auth_required
    @api.expect(a_recommendation)
    def patch(self, id):
        """
        Update a Recommendation
        """
        with db.session.no_autoflush:
            req = api.payload
            
            # Fetch Recommendation
            recommendation = Recommendation.query.filter_by(id=id).first()

            if recommendation is None:
                return { 'message': 'Recommendation does not exist'}, 404

            # Check User permission
            current_user = flask_praetorian.current_user()
            if recommendation.user_id != current_user.id:
                return { 'message': 'Unauthorized to edit Recommendation'}, 401

            # Validate        
            try:
                edit_recommendation = recommendation_patch_schema.load(req)
            except ValidationError as err:
                return { 'error': err.messages }

            # Edit Recommendation
            recommendation.content = edit_recommendation.content

            try:
                db.session.commit()
            except Exception:
                return { 'message': 'Unable to edit Recommendation'}, 500

            return { 'message': 'Recommendation updated successfully' }

    @flask_praetorian.auth_required
    def delete(self, id):
        """
        Delete a Recommendation by id
        """

        # Fetch Recommendation
        recommendation = Recommendation.query.filter_by(id=id).first()
        if recommendation is None:
            return { 'message': 'Recommendation does not exist'}, 404

        # Check User permission
        current_user = flask_praetorian.current_user()
        if recommendation.user_id != current_user.id:
            return { 'message': 'Unauthorized to delete Recommendation'}, 401
            
        try:
            db.session.delete(recommendation)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Recommendation'}, 500
        
        return { 'message': 'Recommendation deleted successfully' }

@api.route('/game/<int:id>', defaults={ 'page': 1 }, methods=['GET'])
@api.route('/game/<int:id>/page/<int:page>', methods=['GET'])
class GameRecommendations(Resource):
    def get(self, page, id):
        """
        List Game Recommendations
        """
        page = page
        per_page = 8

        recommendations = Recommendation.query.filter(Recommendation.game_id==id).order_by(Recommendation.created_at.desc()).paginate(page,per_page,error_out=False)
        response = {
            'items': recommendations_schema.dump(recommendations.items),
            'has_next': recommendations.has_next,
            'has_prev': recommendations.has_prev,
            'next_num': recommendations.next_num,
            'prev_num': recommendations.prev_num,
            'page': recommendations.page,
            'per_page': recommendations.per_page,
            'pages': recommendations.pages,
            'total': recommendations.total       
        }
        return response

@api.route('/user/<int:id>', defaults={ 'page': 1 }, methods=['GET'])
@api.route('/user/<int:id>/page/<int:page>', methods=['GET'])
class UserRecommendations(Resource):
    def get(self, page, id):
        """
        List User Reviews
        """
        page = page
        per_page = 8

        recommendations = Recommendation.query.filter(Recommendation.user_id==id).order_by(Recommendation.created_at.desc()).paginate(page,per_page,error_out=False)
        response = {
            'items': recommendations_schema.dump(recommendations.items),
            'has_next': recommendations.has_next,
            'has_prev': recommendations.has_prev,
            'next_num': recommendations.next_num,
            'prev_num': recommendations.prev_num,
            'page': recommendations.page,
            'per_page': recommendations.per_page,
            'pages': recommendations.pages,
            'total': recommendations.total       
        }
        return response