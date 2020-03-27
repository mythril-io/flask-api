from models import *
from extensions import ma, db
from marshmallow import fields, validate

# DateTypeSchema
class DateTypeSchema(ma.ModelSchema):  
    class Meta:
        model = DateType
        sqla_session = db.session
        fields = ("id", "format")

date_type_schema = DateTypeSchema()
date_types_schema = DateTypeSchema(many=True)

# DeveloperSchema
class DeveloperSchema(ma.ModelSchema):   
    class Meta:
        model = Developer
        sqla_session = db.session
        fields = ("id", "name", "country")

developer_schema = DeveloperSchema()
developers_schema = DeveloperSchema(many=True)

# GenreSchema
class GenreSchema(ma.ModelSchema):
    class Meta:
        model = Genre
        sqla_session = db.session
        fields = ("id", "name", "acronym")

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

# PlatformSchema
class PlatformSchema(ma.ModelSchema):  
    class Meta:
        model = Platform
        sqla_session = db.session
        fields = ("id", "name", "acronym")

platform_schema = PlatformSchema()
platforms_schema = PlatformSchema(many=True)

# PublisherSchema
class PublisherSchema(ma.ModelSchema): 
    class Meta:
        model = Publisher
        sqla_session = db.session
        fields = ("id", "name", "country")

publisher_schema = PublisherSchema()
publishers_schema = PublisherSchema(many=True)

# RegionSchema
class RegionSchema(ma.ModelSchema):  
    class Meta:
        model = Region
        sqla_session = db.session
        fields = ("id", "name", "acronym")

region_schema = RegionSchema()
regions_schema = RegionSchema(many=True)

# RoleSchema
class RoleSchema(ma.ModelSchema):  
    class Meta:
        model = Role
        sqla_session = db.session
        fields = ("id", "name")

role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)

# PlayStatusSchema
class PlayStatusSchema(ma.ModelSchema):  
    class Meta:
        model = PlayStatus
        sqla_session = db.session
        fields = ("id", "name")

play_status_schema = PlayStatusSchema()
play_statuses_schema = PlayStatusSchema(many=True)

# UserSchema
class UserSchema(ma.ModelSchema):
    email = fields.Email(required=True, load_only=True)
    username = fields.String(required=True, validate=[validate.Length(min=4, max=250)])
    password = fields.String(required=True, validate=[validate.Length(min=8, max=250)], load_only=True)
    followers = fields.Nested(lambda: nested_user_schema, many=True)
    following = fields.Nested(lambda: nested_user_schema, many=True)

    class Meta:
        model = User
        sqla_session = db.session
        fields = ("id", "username", "rolenames", "about_me", "avatar", "banner", "timezone", "birthday", "gender", "location", "created_at")

user_schema = UserSchema()
users_schema = UserSchema(only=("id", "username", "avatar", "rolenames"), many=True)
nested_user_schema = UserSchema(only=("id", "username", "avatar", "rolenames"))

# ReleaseSchema
class ReleaseSchema(ma.ModelSchema):
    platform = fields.Nested(platform_schema)
    publisher = fields.Nested(publisher_schema)
    codeveloper = fields.Nested(developer_schema, allow_none=True)
    date_type = fields.Nested(date_type_schema, allow_none=True)
    region = fields.Nested(region_schema)

    class Meta:
        model = Release
        sqla_session = db.session
        fields = ("id", "alternate_title", "platform", "publisher", "codeveloper", "region", "date", "date_type")

release_schema = ReleaseSchema(session=db.session)
releases_schema = ReleaseSchema(many=True, session=db.session)

# GameSchema
class GameSchema(ma.ModelSchema):
    developer = fields.Nested(developer_schema)
    genres = fields.Nested(genres_schema)
    releases = fields.Nested(releases_schema)
    user = fields.Nested(user_schema)

    class Meta:
        model = Game
        sqla_session = db.session
        fields = ("id", "title", "synopsis", "icon", "banner", "developer", "genres", "releases", "score", "library_count", "score_rank", "popularity_rank", "trending_page_views", "user")

game_schema = GameSchema(exclude=['user'])
games_schema = GameSchema(many=True, exclude=['releases'])
nested_game_schema = GameSchema(only=("id", "title", "synopsis", "icon", "banner", "developer"))

# LibraryEntrySchema
class LibraryEntrySchema(ma.ModelSchema):
    game = fields.Nested(nested_game_schema)
    release = fields.Nested(release_schema)
    user = fields.Nested(user_schema)
    play_status = fields.Nested(play_status_schema)
    notes = fields.String(allow_none=True)
    hours = fields.Integer(allow_none=True)
    score = fields.Integer(allow_none=True)

    class Meta:
        model = LibraryEntry
        sqla_session = db.session

library_entry_schema = LibraryEntrySchema()
library_entries_schema = LibraryEntrySchema(many=True)
library_entry_post_schema = LibraryEntrySchema(only=("game.id", "digital", "play_status", "score", "user", "release", "own", "notes", "hours"))
library_entry_patch_schema = LibraryEntrySchema(only=("id", "digital", "play_status", "score", "own", "notes", "hours"))    

# ReviewSchema
class ReviewSchema(ma.ModelSchema):
    summary = fields.String(required=True, validate=[validate.Length(min=60, max=255)])
    content = fields.String(required=True, validate=[validate.Length(min=500)])
    score = fields.Int(required=True, validate=validate.Range(min=1, max=100))
    user = fields.Nested(user_schema)
    game = fields.Nested(nested_game_schema)
    release = fields.Nested(release_schema)

    class Meta:
        model = Review
        sqla_session = db.session

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)
review_post_schema = ReviewSchema(only=("game.id", "summary", "content", "score", "user", "release"))
review_patch_schema = ReviewSchema(only=("id", "summary", "content"))   

# RecommendationSchema
class RecommendationSchema(ma.ModelSchema):
    content = fields.String(required=True, validate=[validate.Length(min=200)])
    user = fields.Nested(user_schema)
    game = fields.Nested(nested_game_schema)
    release = fields.Nested(release_schema)
    recommended_game = fields.Nested(nested_game_schema)
    recommended_release = fields.Nested(release_schema)

    class Meta:
        model = Recommendation
        sqla_session = db.session

recommendation_schema = RecommendationSchema()
recommendations_schema = RecommendationSchema(many=True)
recommendation_post_schema = RecommendationSchema(only=("content", "user", "game.id", "release", "recommended_game.id", "recommended_release"))
recommendation_patch_schema = RecommendationSchema(only=("id", "content"))   

# FavouriteSchema
class FavouriteSchema(ma.ModelSchema):
    user = fields.Nested(user_schema)
    game = fields.Nested(nested_game_schema)
    release = fields.Nested(release_schema)

    class Meta:
        model = Favourite
        sqla_session = db.session

favourite_schema = FavouriteSchema()
favourites_schema = FavouriteSchema(exclude=("user",), many=True)
favourite_post_schema = FavouriteSchema(only=("game.id", "user", "release"))
favourite_patch_schema = FavouriteSchema(only=("release",))

# TagSchema
class TagSchema(ma.ModelSchema):
    parent = fields.Nested(lambda: TagSchema(exclude=("parent",)), allow_none=True)

    class Meta:
        model = Tag
        sqla_session = db.session
        fields = ("id", "name", "slug", "colour", "order", "parent")

tag_schema = TagSchema()
tags_schema = TagSchema(many=True)



# PostSchema
class PostSchema(ma.ModelSchema):
    user = fields.Nested(nested_user_schema)
    discussion_id = fields.Integer()
    parent_post_id = fields.Integer()
    parent_post = fields.Nested(lambda: PostSchema(exclude=("parent_post",)), allow_none=True)

    class Meta:
        model = Post
        sqla_session = db.session

post_schema = PostSchema()
post_post_schema = PostSchema(only=("body", "discussion_id", "parent_post_id"))
post_patch_schema = PostSchema(only=("body",))

# DiscussionSchema
class DiscussionSchema(ma.ModelSchema):
    user = fields.Nested(nested_user_schema)
    games = fields.Nested(GameSchema(only=("id", "title"), many=True), allow_none=True)
    tags = fields.Nested(tags_schema)
    posts = fields.Nested(PostSchema(exclude=("discussion", "discussion_id", "parent_post_id"),many=True), allow_none=True)

    class Meta:
        model = Discussion
        sqla_session = db.session

discussion_schema = DiscussionSchema()
discussions_schema = DiscussionSchema(many=True)
discussion_post_schema = DiscussionSchema(only=("title", "body", "tags", "games"))
discussion_patch_schema = DiscussionSchema(only=("body", "tags", "games"))