from extensions import db
from datetime import datetime

__all__ = ['Discussion']

discussion_game = db.Table('discussion_game',
    db.Column('discussion_id', db.Integer, db.ForeignKey('discussions.id'), primary_key=True),
    db.Column('game_id', db.Integer, db.ForeignKey('games.id'), primary_key=True),
    extend_existing=True
)

discussion_tag = db.Table('discussion_tag',
    db.Column('discussion_id', db.Integer, db.ForeignKey('discussions.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    extend_existing=True
)

class Discussion(db.Model):
    __tablename__ = 'discussions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    slug = db.Column(db.String, unique=True, nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    view_count = db.Column(db.Integer, nullable=False, index=True, default=0)
    like_count = db.Column(db.Integer, nullable=False, index=True, default=0)
    post_count = db.Column(db.Integer, nullable=False, index=True, default=0)
    user_count = db.Column(db.Integer, nullable=False, index=True, default=0)
    edit_count = db.Column(db.Integer, nullable=False, index=True, default=0)
    edited_at = db.Column(db.DateTime)
    is_pinned = db.Column(db.Integer, nullable=False, default=0)
    is_locked = db.Column(db.Integer, nullable=False, default=0)

    last_post_id = db.Column(db.Integer, index=True)
    last_posted_at = db.Column(db.DateTime, index=True)
    hidden_at = db.Column(db.DateTime)
    hidden_user_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User')
    games = db.relationship('Game', secondary=discussion_game, backref=db.backref('discussions'))
    tags = db.relationship('Tag', secondary=discussion_tag, backref=db.backref('discussions'))
    posts = db.relationship('Post', backref='discussion')

    def __repr__(self):
        return '<Discussion %r>' % self.title

	# `is_subscribed` TINYINT(1) NOT NULL DEFAULT '0',