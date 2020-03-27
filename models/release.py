from extensions import db
from datetime import datetime

__all__ = ['Release']

class Release(db.Model):
    __tablename__ = 'releases'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'), nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'), nullable=False)
    codeveloper_id = db.Column(db.Integer, db.ForeignKey('developers.id'), nullable=True)
    alternate_title = db.Column(db.String, nullable=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=True)
    date = db.Column(db.Date, nullable=True)
    date_type_id = db.Column(db.Integer, db.ForeignKey('date_types.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return '<Release %r>' % self.id