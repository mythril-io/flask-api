from extensions import db
from datetime import datetime

__all__ = ['Tag']

class Tag(db.Model):
    __tablename__ = 'tags'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    slug = db.Column(db.String, unique=True, nullable=False)
    colour = db.Column(db.String, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    order = db.Column(db.Integer)
    is_restricted = db.Column(db.Integer, nullable=False, default=0)
    is_hidden = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)
    
    # discussions_count = db.Column(db.Integer, nullable=False, default=0)
    # last_posted_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # last_posted_discussion_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Tag %r>' % self.name