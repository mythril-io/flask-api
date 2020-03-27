from flask_restx import Namespace, Resource
from extensions import guard, db
from marshmallow import ValidationError
from sqlalchemy.sql.functions import func

from models import Game, Review, Recommendation, LibraryEntry, User, Release
from .schemas import game_schema, games_schema, review_schema, recommendation_schema, library_entries_schema
from . import api as api_v1

api = Namespace('home', description='Home page operations')

@api.route('/')
class Home(Resource):
    def get(self):
        """
        Get all Resources used on the Home page
        """
        game = Game.query.filter_by(id=295).first()
        trending = Game.query.order_by(Game.trending_page_views.desc()).limit(6).all()
        review = Review.query.order_by(Review.created_at.desc()).limit(1).first()
        recommendation = Recommendation.query.order_by(Recommendation.created_at.desc()).limit(1).first()
        recent_user_activity = LibraryEntry.query.order_by(LibraryEntry.created_at.desc()).limit(8).all()

        game_count = db.session.query(func.count(Game.id)).first()[0]
        releases_count = db.session.query(func.count(Release.id)).first()[0]
        review_count = db.session.query(func.count(Review.id)).first()[0]
        recommendation_count = db.session.query(func.count(Recommendation.id)).first()[0]
        user_count = db.session.query(func.count(User.id)).first()[0]

        stats = {
            'games': game_count,
            'releases': releases_count,
            'reviews': review_count,
            'recommendations': recommendation_count,
            'users': user_count,
        }

        response = {
            'game': game_schema.dump(game),
            'trending': games_schema.dump(trending),
            'review': review_schema.dump(review),
            'recommendation': recommendation_schema.dump(recommendation),
            'stats': stats,
            'recent_user_activity': library_entries_schema.dump(recent_user_activity)
        }
        return response