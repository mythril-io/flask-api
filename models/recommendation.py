from extensions import db
from datetime import datetime

__all__ = ['Recommendation']

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    release_id = db.Column(db.Integer, db.ForeignKey('releases.id'), nullable=False)
    second_game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    second_release_id = db.Column(db.Integer, db.ForeignKey('releases.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User')
    game = db.relationship('Game', foreign_keys=[game_id])
    release = db.relationship('Release', foreign_keys=[release_id])
    recommended_game = db.relationship('Game', foreign_keys=[second_game_id])
    recommended_release = db.relationship('Release', foreign_keys=[second_release_id])

    def __repr__(self):
        return '<Recommendation %r>' % self.id