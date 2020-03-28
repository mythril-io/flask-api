from flask_restx import Namespace, Resource
from extensions import guard, db
from marshmallow import ValidationError
from sqlalchemy.sql.functions import func

from models import Game, Review, Recommendation, LibraryEntry, User, Release
from . import api as api_v1

api = Namespace('home', description='Home page operations')

@api.route('/')
class Home(Resource):
    def getStats(self):
        """
        Get all Stats used on the Home page
        """
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
            'stats': stats,
        }
        
        return response