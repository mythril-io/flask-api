import flask_praetorian
from flask import request
from flask_restx import Namespace, Resource, Api, fields
from extensions import guard, db, upload_img, delete_img
from marshmallow import ValidationError, INCLUDE
from utilities import get_auto_increment, base64_to_pillow_img, pillow_img_to_bytes
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_

from models import Game, Genre, User, Release
from .schemas import games_schema, game_schema, genres_schema, user_schema, GameSchema
from . import api as api_v1

api = Namespace('games', description='Game operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_game = api_v1.model('Game', {
    'title': fields.String(required=True, description='Title'),
    'synopsis': fields.String(required=True, description='Synopsis'),
})

@api.route('/search')
class SearchGames(Resource):
    def get(self):
        """
        Get 25 Games that match search criteria
        """
        query = request.args.get('query') or ''
        games = Game.query.filter(Game.title.like('%' + query + '%')).limit(25).all()
        return GameSchema(many=True, exclude=['user']).dump(games)

@api.route('/', defaults={ 'page': 1 }, methods=['GET'])
@api.route('/', methods=['POST'])
@api.route('/page/<int:page>', methods=['GET'])
class Games(Resource):
    def get(self, page):
        """
        List Games using pagination and applicable filters
        """
        page = page
        per_page = 8

        # Request Parameters (Filters applied)
        search = request.args.get('search') or ''
        score = request.args.get('score') or 0
        developer_ids = request.args.get('developers') or None
        publisher_ids = request.args.get('publishers') or None
        platform_ids = request.args.get('platforms') or None
        genre_ids = request.args.get('genres') or None
        
        # Prepare query
        query = Game.query

        # Apply filters if applicable
        if search:
            query = query.filter(Game.title.like('%' + search + '%'))
        if score and int(score) > 0:
            query = query.filter(Game.score >= score)
        if developer_ids:
            developer_list = developer_ids.split(",")
            query = query.filter(or_(
                Game.developer_id.in_((developer_list)), # Primary Developers
                Game.releases.any(Release.codeveloper_id.in_((developer_list))) # Codevelopers
            ))
        if publisher_ids:
            publisher_list = publisher_ids.split(",")
            query = query.filter(Game.releases.any(Release.publisher_id.in_((publisher_list))))
        if platform_ids:
            platform_list = platform_ids.split(",")
            query = query.filter(Game.releases.any(Release.platform_id.in_((platform_list))))
        if genre_ids:
            genre_list = genre_ids.split(",")
            query = query.filter(Game.genres.any(Genre.id.in_((genre_list))))

        # Execute query
        games = query.order_by(Game.popularity_rank.asc()).paginate(page,per_page,error_out=False)

        response = {
            'items': games_schema.dump(games.items),
            'has_next': games.has_next,
            'has_prev': games.has_prev,
            'next_num': games.next_num,
            'prev_num': games.prev_num,
            'page': games.page,
            'per_page': games.per_page,
            'pages': games.pages,
            'total': games.total       
        }
        return response

    @flask_praetorian.roles_required('admin')
    def post(self):
        with db.session.no_autoflush:
            """
            Add new Game
            """
            req = api.payload
            
            # Set Authenticated User
            current_user = flask_praetorian.current_user()
            req['user'] = user_schema.dump(current_user)
            
            # Validate        
            try:
                new_game = game_schema.load(req)
            except ValidationError as err:
                return { 'error': err.messages }

            # Retrieve auto increment value for "games" table
            try:
                AUTO_INCREMENT = get_auto_increment('GAMES')
            except IndexError:
                return { 'error': 'Unable to retrieve database auto increment value' }, 500

            # Upload Icon
            icon_base64_string = req['icon'].split(',')[1]
            icon = base64_to_pillow_img(icon_base64_string)
            icon_file_name = '{}.{}'.format(AUTO_INCREMENT, icon.format.lower())
            icon_bytes = pillow_img_to_bytes(icon)
            upload_img(icon_bytes, icon.format.lower(), Key=icon_file_name, Prefix='games/icons')
            new_game.icon = icon_file_name

            # Upload Banner
            banner_base64_string = req['banner'].split(',')[1]
            banner = base64_to_pillow_img(banner_base64_string)
            banner_file_name = '{}.{}'.format(AUTO_INCREMENT, banner.format.lower())
            banner_bytes = pillow_img_to_bytes(banner)
            upload_img(banner_bytes, banner.format.lower(), Key=banner_file_name, Prefix='games/banners')
            new_game.banner = banner_file_name

            # Perform SQL Insertion Query
            try:
                db.session.add(new_game)
                db.session.commit()
            except SQLAlchemyError:
                delete_img(new_game.icon, Prefix='games/icons')
                delete_img(new_game.banner, Prefix='games/banners')
                db.session.rollback()
                return { 'error': 'Unable to add Game' }, 500
            
            return { 'message': 'Game added successfully' }

@api.route('/<int:id>')
class SingleGame(Resource):
    def get(self, id):
        """
        Get Game by id
        """
        game = Game.query.filter_by(id=id).first()
        game.trending_page_views += 1

        try:
            db.session.commit()
        except SQLAlchemyError:
            return { 'error': 'Unable to update view count' }, 500

        return game_schema.dump(game)
    
    @flask_praetorian.roles_required('admin')
    def put(self, id):
        """
        Update a Game
        """
        with db.session.no_autoflush:
            req = api.payload
            
            # Fetch Game
            game = Game.query.filter_by(id=id).first()
            if game is None:
                return { 'message': 'Game does not exist'}, 404

            icon_name = game.icon
            banner_name = game.banner

            # Validate        
            try:
                edit_game = game_schema.load(req)
            except ValidationError as err:
                return { 'error': err.messages }
            
            # Update Icon
            if edit_game.icon != icon_name:
                icon_base64_string = req['icon'].split(',')[1]
                icon = base64_to_pillow_img(icon_base64_string)
                icon_file_name = '{}.{}'.format(game.id, icon.format.lower())
                icon_bytes = pillow_img_to_bytes(icon)
                delete_img(icon_name, Prefix='games/icons')
                upload_img(icon_bytes, icon.format.lower(), Key=icon_file_name, Prefix='games/icons')
                edit_game.icon = icon_file_name

            # Update Banner
            if edit_game.banner != banner_name:
                banner_base64_string = req['banner'].split(',')[1]
                banner = base64_to_pillow_img(banner_base64_string)
                banner_file_name = '{}.{}'.format(game.id, banner.format.lower())
                banner_bytes = pillow_img_to_bytes(banner)
                delete_img(banner_name, Prefix='games/banners')
                upload_img(banner_bytes, banner.format.lower(), Key=banner_file_name, Prefix='games/banners')
                edit_game.banner = banner_file_name

            try:
                # db.session.expunge(edit_game)
                db.session.commit()
            except Exception:
                return { 'message': 'Unable to edit Game'}, 500

            return { 'message': 'Game updated successfully' }

    @flask_praetorian.roles_required('admin')
    def delete(self, id):
        """
        Delete a Game by id
        """
        game = Game.query.filter_by(id=id).first()
        if game is None:
            return { 'message': 'Game does not exist'}, 404

        try:
            db.session.delete(game)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to delete Game'}, 500

        del_icon = delete_img(game.icon, Prefix='games/icons')
        if del_icon["ResponseMetadata"]["HTTPStatusCode"] != 204:
            return { 'message': 'Unable to delete icon'}, 500

        del_banner = delete_img(game.banner, Prefix='games/banners')
        if del_banner["ResponseMetadata"]["HTTPStatusCode"] != 204:
            return { 'message': 'Unable to delete banner'}, 500
        
        return { 'message': 'Game deleted successfully' }

@api.route('/trending')
class TrendingGames(Resource):
    def get(self):
        """
        Get Trending Games
        """
        games = Game.query.order_by(Game.trending_page_views.desc()).limit(6).all()

        return games_schema.dump(games)

@api.route('/icon/<int:id>')
class GameIcon(Resource):  
    @flask_praetorian.roles_required('admin')
    def patch(self, id):
        """
        Update a Game Icon
        """
        with db.session.no_autoflush:
            req = api.payload

            # Fetch Game
            game = Game.query.filter_by(id=id).first()
            if game is None:
                return { 'message': 'Game does not exist'}, 404

            # Validate
            # Call method to check if string is base64 and png/jpg/gif  
            # return { 'message': 'Icon not valid'}, 404   

            # Update Icon
            icon = base64_to_pillow_img(req['icon'])
            icon_file_name = '{}.{}'.format(game.id, icon.format.lower())
            icon_bytes = pillow_img_to_bytes(icon)
            delete_img(game.icon, Prefix='games/icons')
            upload_img(icon_bytes, icon.format.lower(), Key=icon_file_name, Prefix='games/icons')
            game.icon = icon_file_name                

            try:
                db.session.commit()
            except Exception:
                return { 'message': 'Unable to edit Game icon'}, 500

            return { 'message': 'Game icon updated successfully' }