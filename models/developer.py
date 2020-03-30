from extensions import db
from datetime import datetime

__all__ = ['Developer']

class Developer(db.Model):
    __tablename__ = 'developers'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=True)
    releases = db.relationship('Release', backref='codeveloper')
    games = db.relationship('Game', backref='developer')
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return '<Developer %r>' % self.name