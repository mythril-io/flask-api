from extensions import db
from datetime import datetime

__all__ = ['Favourite']

class Favourite(db.Model):
    __tablename__ = 'favourites'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    release_id = db.Column(db.Integer, db.ForeignKey('releases.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User')
    game = db.relationship('Game')
    release = db.relationship('Release')

    def __repr__(self):
        return '<Favourite %r>' % self.id