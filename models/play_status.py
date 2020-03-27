from extensions import db
from datetime import datetime

__all__ = ['PlayStatus']

class PlayStatus(db.Model):
    __tablename__ = 'play_statuses'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return '<PlayStatus %r>' % self.name