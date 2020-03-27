from extensions import db
from datetime import datetime

__all__ = ['LibraryEntry']

class LibraryEntry(db.Model):
    __tablename__ = 'libraries'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    release_id = db.Column(db.Integer, db.ForeignKey('releases.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    play_status_id = db.Column(db.Integer, db.ForeignKey('play_statuses.id'), nullable=False)
    score = db.Column(db.Integer)
    own = db.Column(db.Integer, nullable=False, default=1)
    digital = db.Column(db.Integer, nullable=False, default=0)
    hours = db.Column(db.Integer)
    notes = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)

    game = db.relationship('Game')
    release = db.relationship('Release')
    user = db.relationship('User')
    play_status = db.relationship('PlayStatus')
    
    def __repr__(self):
        return '<LibraryEntry %r>' % self.id