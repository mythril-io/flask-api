from extensions import db
from datetime import datetime

__all__ = ['Post']

class Post(db.Model):
    __tablename__ = 'posts'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'), nullable=False)
    parent_post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    edit_count = db.Column(db.Integer, nullable=False, index=True, default=0)
    hidden_at = db.Column(db.DateTime)
    hidden_user_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User')
    parent_post = db.relationship('Post')

    def __repr__(self):
        return '<Post %r>' % self.id

	# `number` INT(10) UNSIGNED NULL DEFAULT NULL,