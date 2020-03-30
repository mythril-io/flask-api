from extensions import db
from datetime import datetime

__all__ = ['DateType']

class DateType(db.Model):
    __tablename__ = 'date_types'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    format = db.Column(db.String, nullable=False)
    releases = db.relationship('Release', backref='date_type')
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return '<DateType %r>' % self.format