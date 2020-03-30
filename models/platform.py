from extensions import db
from datetime import datetime

__all__ = ['Platform']

class Platform(db.Model):
    __tablename__ = 'platforms'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    acronym = db.Column(db.String, nullable=True)
    releases = db.relationship('Release', backref='platform')
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return '<Platform %r>' % self.name