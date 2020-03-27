import flask_praetorian
from flask import current_app as app
from flask_restx import Namespace, Resource, Api, reqparse, fields
from extensions import guard, db, upload_img, delete_img
from marshmallow import ValidationError, INCLUDE
from utilities import base64_to_pillow_img, pillow_img_to_bytes, base64_validation, get_base64_file_type


from models import User
from .schemas import users_schema, user_schema, roles_schema
from . import api as api_v1

api = Namespace('users', description='User operations')

# Required for proper Swagger documentation via Flask RESTPlus (Deserialization is completed by marshmallow)
a_user = api_v1.model('User', {
    'email': fields.String(required=True, description='E-mail'),
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password'),
    'about_me': fields.String(required=False, description='About the user'),
})

@api.route('/')
class UserList(Resource):
    def get(self):
        """
        List Users
        """
        users = User.query.all()
        return users_schema.dump(users)

@api.route('/<int:id>')
class SingleUser(Resource):
    def get(self, id):
        """
        List User by id
        """
        user = User.query.filter_by(id=id).first()
        if user is None:
            return { 'message': 'User does not exist'}, 404

        return user_schema.dump(user)

@api.route('/login')
class Login(Resource):
    @api.expect(a_user)
    def post(self):
        """
        Login user and issue JWT token
        """

        req = api.payload
        username = req.get('username', None)
        password = req.get('password', None)
        user = guard.authenticate(username, password)

        if user.is_verified != 1:
            return { 'message': 'Please verify your email.'}, 403

        response = {
            'user': user_schema.dump(user),
            'access_token': guard.encode_jwt_token(user)
        }
        return response

@api.route('/refresh')
class Refresh(Resource):
    def get(self):
        """
        Refresh an existing JWT token by creating a new token from the copy of the old one with a refreshed access expiration
        """
        old_token = guard.read_token_from_header()
        new_token = guard.refresh_jwt_token(old_token)

        response = {
            'access_token': new_token 
        }
        return response

    def post(self):
        """
        Refresh an existing JWT token by creating a new token from the copy of the old one with a refreshed access expiration
        """
        req = api.payload
        email = req.get('email', None)

        user = User.query.filter_by(email=email).scalar()
        if user is None:
            return { 'message': 'E-mail address is not registered'}, 404

        if user.is_verified == 1:
            return { 'message': 'Account associated with that e-mail address is already verified'}, 403

        try:
            guard.send_registration_email(email, user=user)
        except Exception:
            return { 'message': 'Unable to send verification e-mail'}, 500
        
        return { 'message': 'Successfully sent verification email to {}'.format(email) }

@api.route('/register')
@api.doc(params={'username': 'Username', 'password': 'Password', 'email': 'E-mail'})
class Register(Resource):
    @api.expect(a_user)
    def post(self):
        """
        Register a new user and dispatch an email with a registration token
        """
        req = api.payload
        
        try:
            user_schema.load(req, unknown=INCLUDE)
        except ValidationError as err:
            return { 'error': err.messages }

        username = req.get('username', None)
        email = req.get('email', None)
        password = req.get('password', None)
        new_user = User(
            username=username,
            password=guard.hash_password(password),
            email=email,
        )

        username_exists = User.query.filter_by(username=username).scalar() is not None
        if (username_exists):
            return { 'message': 'Username already in use'}, 500

        email_exists = User.query.filter_by(email=email).scalar() is not None
        if (email_exists):
            return { 'message': 'E-mail already in use'}, 500

        try:
            db.session.add(new_user)
            db.session.commit()
            guard.send_registration_email(email, user=new_user)
        except Exception:
            return { 'message': 'Unable to register new account'}, 500


        response = {'message': 'Successfully sent verification email to user {}'.format(
            new_user.username
        )}
        return response

    def get(self):
        """
        Verifies a user registration with registration token
        """
        registration_token = guard.read_token_from_header()
        user = guard.get_user_from_registration_token(registration_token)

        # Activate User
        db_user = User.query.filter_by(id=user.id).first()
        db_user.is_verified = 1
        db.session.commit()

        response = {
            'user': user_schema.dump(user),
            'access_token': guard.encode_jwt_token(user)
        }
        return response  

@api.route('/follow/<int:id>')
class follow(Resource):
    @flask_praetorian.auth_required
    @api.expect(a_user)
    def post(self, id):
        """
        Follow a User by id
        """
        req = api.payload

        # Get Authenticated User
        current_user = flask_praetorian.current_user()
    
        # Get User to follow        
        user = User.query.filter_by(id=id).first()
        if user is None:
            return { 'message': 'User does not exist'}, 404

        # Check if current_user is already following specified user
        if user in current_user.following:
            return { 'message': 'Already following User'}, 403

        # Follow User
        try:
            current_user.following.append(user)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to follow User'}, 500
        
        return { 'data': user_schema.dump(current_user) }

    @flask_praetorian.auth_required
    def delete(self, id):
        """
        Unfollow a User by id
        """
        # Validate
        user = User.query.filter_by(id=id).first()
        if user is None:
            return { 'message': 'User does not exist'}, 404

        # Get Authenticated User
        current_user = flask_praetorian.current_user()

        # Check if current_user is following specified user
        if user not in current_user.following:
            return { 'message': 'User is not being followed'}, 403
            
        try:
            current_user.following.remove(user)
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to unfollow User'}, 500
        
        return { 'message': 'User unfollowed successfully' }

@api.route('/<int:id>/following')
class UserFollowing(Resource):
    def get(self, id):
        """
        List User Following
        """
        user = User.query.filter_by(id=id).first()
        if user is None:
            return { 'message': 'User does not exist'}, 404

        users = user.following

        return users_schema.dump(users)

@api.route('/<int:id>/followers')
class UserFollowers(Resource):
    def get(self, id):
        """
        List User Followers
        """
        user = User.query.filter_by(id=id).first()
        if user is None:
            return { 'message': 'User does not exist'}, 404

        users = user.followers

        return users_schema.dump(users)

@api.route('/<int:id>/follow-status')
class FollowStatus(Resource):
    @flask_praetorian.auth_required
    def get(self, id):
        """
        Check if authenticated user if following specified user
        """
        current_user = flask_praetorian.current_user()

        user = User.query.filter_by(id=id).first()
        if user is None:
            return { 'message': 'User does not exist'}, 404

        status = any(x for x in user.followers if x.id == current_user.id)

        return { 'status': status }

@api.route('/<int:id>/details')
class UserDetails(Resource):
    @flask_praetorian.auth_required
    def patch(self, id):
        """
        Update User Details
        """
        req = api.payload

        user = User.query.filter_by(id=id).first()
        if user is None:
            return { 'message': 'User does not exist'}, 404

        # Check User permission
        current_user = flask_praetorian.current_user()
        if user.id != current_user.id:
            return { 'message': 'Unauthorized to edit details'}, 401

        # Edit Details
        user.about_me = req.get('about_me')
        user.location = req.get('location')
        user.gender = req.get('gender')
        user.timezone = req.get('timezone')
        user.birthday = req.get('birthday')

        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit Details'}, 500

        response = {
            'user': user_schema.dump(user),
            'message': 'Details updated successfully'
        }

        return response

@api.route('/avatar')
class UserAvatar(Resource):
    @flask_praetorian.auth_required
    def patch(self):
        """
        Update User Avatar
        """
        req = api.payload

        # Check User permission
        user = flask_praetorian.current_user()
        if user is None:
            return { 'message': 'Unauthorized to edit avatar'}, 401

        img_base64_string = req['image'].split(',')[1]
        file_type = get_base64_file_type(img_base64_string)

        # Validate      
        validation = base64_validation(img_base64_string, app.config['MAX_USER_AVATAR_SIZE'])
        if validation == False:
            return { 'message': 'Exceeds file size limit or incorrect file type'}, 403
    
        # Edit Avatar
        img = base64_to_pillow_img(img_base64_string, max_width=500)
        img_file_name = '{}.{}'.format(user.id, file_type)
        img_bytes = pillow_img_to_bytes(img, file_type)
        if user.avatar:
            delete_img(user.avatar, Prefix='users/avatars')
        upload_img(img_bytes, file_type, Key=img_file_name, Prefix='users/avatars')
        user.avatar = img_file_name

        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit avatar'}, 500

        response = {
            'user': user_schema.dump(user),
            'message': 'Avatar updated successfully'
        }

        return response

@api.route('/banner')
class UserBanner(Resource):
    @flask_praetorian.auth_required
    def patch(self):
        """
        Update User Banner
        """
        req = api.payload

        # Check User permission
        user = flask_praetorian.current_user()
        if user is None:
            return { 'message': 'Unauthorized to edit banner'}, 401

        img_base64_string = req['image'].split(',')[1]
        file_type = get_base64_file_type(img_base64_string)

        # Validate      
        validation = base64_validation(img_base64_string, app.config['MAX_USER_BANNER_SIZE'])
        if validation == False:
            return { 'message': 'Exceeds file size limit or incorrect file type'}, 403
    
        # Edit Banner
        img = base64_to_pillow_img(img_base64_string)
        img_file_name = '{}.{}'.format(user.id, file_type)
        img_bytes = pillow_img_to_bytes(img, file_type)
        if user.banner:
            delete_img(user.banner, Prefix='users/banners')
        upload_img(img_bytes, file_type, Key=img_file_name, Prefix='users/banners')
        user.banner = img_file_name

        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit banner'}, 500

        response = {
            'user': user_schema.dump(user),
            'message': 'Banner updated successfully'
        }

        return response

@api.route('/password')
class UserPassword(Resource):
    @flask_praetorian.auth_required
    def patch(self):
        """
        Update User Password
        """
        req = api.payload

        # Check User permission
        user = flask_praetorian.current_user()

        # Edit Password
        password = req.get('password')
        password_hash = guard.hash_password(password)
        user.password = password_hash

        try:
            db.session.commit()
        except Exception:
            return { 'message': 'Unable to edit password'}, 500

        response = {
            'message': 'Password updated successfully'
        }

        return response