from flask import Blueprint
from flask_restx import Api

blueprint = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api = Api(blueprint,
    title='Mythril API v1',
    version='1.0',
    description='Mythril API endpoints',
)

# Import API namespaces
from api.v1.users import api as users_namespace
from api.v1.games import api as games_namespace
from api.v1.releases import api as releases_namespace
from api.v1.roles import api as roles_namespace
from api.v1.platforms import api as platforms_namespace
from api.v1.regions import api as regions_namespace
from api.v1.date_types import api as date_types_namespace
from api.v1.developers import api as developers_namespace
from api.v1.publishers import api as publishers_namespace
from api.v1.play_statuses import api as play_statuses_namespace
from api.v1.libraries import api as libraries_namespace
from api.v1.genres import api as genres_namespace
from api.v1.reviews import api as reviews_namespace
from api.v1.recommendations import api as recommendations_namespace
from api.v1.favourites import api as favourites_namespace
from api.v1.tags import api as tags_namespace
from api.v1.discussions import api as discussions_namespace
from api.v1.posts import api as posts_namespace
from api.v1.home import api as home_namespace

# Register API namespaces
api.add_namespace(users_namespace)
api.add_namespace(games_namespace)
api.add_namespace(releases_namespace)
api.add_namespace(roles_namespace)
api.add_namespace(platforms_namespace)
api.add_namespace(regions_namespace)
api.add_namespace(date_types_namespace)
api.add_namespace(developers_namespace)
api.add_namespace(publishers_namespace)
api.add_namespace(play_statuses_namespace)
api.add_namespace(libraries_namespace)
api.add_namespace(genres_namespace)
api.add_namespace(reviews_namespace)
api.add_namespace(recommendations_namespace)
api.add_namespace(favourites_namespace)
api.add_namespace(tags_namespace)
api.add_namespace(discussions_namespace)
api.add_namespace(posts_namespace)
api.add_namespace(home_namespace)