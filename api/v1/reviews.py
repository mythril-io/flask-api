import flask_praetorian
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db
from marshmallow import ValidationError

from models import Review
from .schemas import review_schema, reviews_schema, user_schema, review_post_schema, review_patch_schema
from . import api as api_v1
from api.v1.likeables import Likeables

api = Namespace('reviews', description='Review operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_review = api_v1.model('Review', {
    'summary': fields.String(required=True, description='Summary'),
    'content': fields.String(required=True, description='Content'),
    'score': fields.Integer(required=True, description='Score'),
})

@api.route('/all')
class AllReviews(Resource):
    def get(self):
        """
        Get all Reviews
        """
        reviews = Review.query.all()
        return reviews_schema.dump(reviews)

@api.route('/', defaults={ 'page': 1 }, methods=['GET'])
@api.route('/', methods=['POST'])
@api.route('/page/<int:page>', methods=['GET'])
class Reviews(Resource):
    def get(self, page):
        """
        List Reviews
        """
        page = page
        per_page = 8

        reviews = Review.query.order_by(Review.created_at.desc()).paginate(page,per_page,error_out=False)
        response = {
            'items': reviews_schema.dump(reviews.items),
            'has_next': reviews.has_next,
            'has_prev': reviews.has_prev,
            'next_num': reviews.next_num,
            'prev_num': reviews.prev_num,
            'page': reviews.page,
            'per_page': reviews.per_page,
            'pages': reviews.pages,
            'total': reviews.total       
        }
        return response

    @flask_praetorian.auth_required
    @api.expect(a_review)
    def post(self):
        """
        Add new Review
        """
        req = api.payload

        # Set Authenticated User
        current_user = flask_praetorian.current_user()
        req['user'] = user_schema.dump(current_user)
        
        # Validate        
        try:
            new_review = review_post_schema.load(req)
        except ValidationError as err:
            return { 'error': err.messages }       

        # Add Review
        try:
            db.session.add(new_review)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to add Review'}, 500
        
        return review_schema.dump(new_review), 201

@api.route('/<int:id>')
class SingleReview(Resource):
    def get(self, id):
        """
        Get Review by id
        """
        review = Review.query.filter_by(id=id).first()
        if review is None:
            return { 'message': 'Review does not exist'}, 404

        return review_schema.dump(review)

    @flask_praetorian.auth_required
    @api.expect(a_review)
    def patch(self, id):
        """
        Update a Review
        """
        with db.session.no_autoflush:
            req = api.payload
            
            # Fetch Review
            review = Review.query.filter_by(id=id).first()

            if review is None:
                return { 'message': 'Review does not exist'}, 404

            # Check User permission
            current_user = flask_praetorian.current_user()
            if review.user_id != current_user.id:
                return { 'message': 'Unauthorized to edit Review'}, 401

            # Validate        
            try:
                edit_review = review_patch_schema.load(req)
            except ValidationError as err:
                return { 'error': err.messages }

            # Edit Review
            review.summary = edit_review.summary
            review.content = edit_review.content

            try:
                db.session.commit()
            except Exception:
                return { 'message': 'Unable to edit Review'}, 500

            return { 'message': 'Review updated successfully' }

    @flask_praetorian.auth_required
    def delete(self, id):
        """
        Delete a Review by id
        """

        # Fetch Review
        review = Review.query.filter_by(id=id).first()
        if review is None:
            return { 'message': 'Review does not exist'}, 404

        # Check User permission
        current_user = flask_praetorian.current_user()
        if review.user_id != current_user.id:
            return { 'message': 'Unauthorized to delete Review'}, 401
            
        try:
            db.session.delete(review)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Review'}, 500
        
        return { 'message': 'Review deleted successfully' }

@api.route('/recent')
class RecentReview(Resource):
    def get(self):
        """
        Get Recent Review
        """
        review = Review.query.order_by(Review.created_at.desc()).limit(1).first()
        
        return review_schema.dump(review)

@api.route('/game/<int:id>', defaults={ 'page': 1 }, methods=['GET'])
@api.route('/game/<int:id>/page/<int:page>', methods=['GET'])
class GameReviews(Resource):
    def get(self, page, id):
        """
        List Game Reviews
        """
        page = page
        per_page = 8

        reviews = Review.query.filter(Review.game_id==id).order_by(Review.created_at.desc()).paginate(page,per_page,error_out=False)
        response = {
            'items': reviews_schema.dump(reviews.items),
            'has_next': reviews.has_next,
            'has_prev': reviews.has_prev,
            'next_num': reviews.next_num,
            'prev_num': reviews.prev_num,
            'page': reviews.page,
            'per_page': reviews.per_page,
            'pages': reviews.pages,
            'total': reviews.total       
        }
        return response

@api.route('/user/<int:id>', defaults={ 'page': 1 }, methods=['GET'])
@api.route('/user/<int:id>/page/<int:page>', methods=['GET'])
class UserReviews(Resource):
    def get(self, page, id):
        """
        List User Reviews
        """
        page = page
        per_page = 8

        reviews = Review.query.filter(Review.user_id==id).order_by(Review.created_at.desc()).paginate(page,per_page,error_out=False)
        response = {
            'items': reviews_schema.dump(reviews.items),
            'has_next': reviews.has_next,
            'has_prev': reviews.has_prev,
            'next_num': reviews.next_num,
            'prev_num': reviews.prev_num,
            'page': reviews.page,
            'per_page': reviews.per_page,
            'pages': reviews.pages,
            'total': reviews.total       
        }
        return response

@api.route('/<int:id>/like')
class LikeReview(Resource):
    @flask_praetorian.auth_required
    def post(self, id):
        """
        Like a Review by id
        """
        current_user = flask_praetorian.current_user()

        # Find Review
        review = Review.query.filter_by(id=id).first()
        if review is None:
            return { 'message': 'Review does not exist'}, 404

        # Like the Review
        status_code = Likeables.create(Likeables, current_user.id, Review.__name__.lower(), review.id, 1)

        if status_code == 500:
            return { 'message': 'Unable to update like status for Review'}, 500
        if status_code == 404:
            return { 'message': 'Unable to find like for Review'}, 404

        # Get likes/dislikes count
        count = Likeables.getCount(Likeables, Review.__name__.lower(), review.id)
        user_sentiment = Likeables.getUserSentiment(Likeables, current_user.id, Review.__name__.lower(), review.id)
        
        response = {
            'like_count': count.get('like_count'),
            'dislike_count': count.get('dislike_count'),
            'user_sentiment': user_sentiment.get('user_sentiment')
        }
        return response

@api.route('/<int:id>/dislike')
class DislikeReview(Resource):
    @flask_praetorian.auth_required
    def post(self, id):
        """
        Disike a Review by id
        """
        current_user = flask_praetorian.current_user()

        # Find Review
        review = Review.query.filter_by(id=id).first()
        if review is None:
            return { 'message': 'Review does not exist'}, 404

        # Dislike the Review
        status_code = Likeables.create(Likeables, current_user.id, Review.__name__.lower(), review.id, 0)

        if status_code == 500:
            return { 'message': 'Unable to update like status for Review'}, 500
        if status_code == 404:
            return { 'message': 'Unable to find dislike for Review'}, 404

        # Get likes/dislikes count
        count = Likeables.getCount(Likeables, Review.__name__.lower(), review.id)
        user_sentiment = Likeables.getUserSentiment(Likeables, current_user.id, Review.__name__.lower(), review.id)
        
        response = {
            'like_count': count.get('like_count'),
            'dislike_count': count.get('dislike_count'),
            'user_sentiment': user_sentiment.get('user_sentiment')
        }
        return response

@api.route('/<int:id>/user-sentiment')
class UserSentiment(Resource):
    @flask_praetorian.auth_required
    def get(self, id):
        """
        Get User like/dislike by Review
        """
        current_user = flask_praetorian.current_user()

        return Likeables.getUserSentiment(Likeables, current_user.id, Review.__name__.lower(), id)