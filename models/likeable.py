from extensions import db
from datetime import datetime

__all__ = ['Likeable']

class Likeable(db.Model):
    __tablename__ = 'likeables'
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, primary_key=True)
    type_id = db.Column(db.Integer, nullable=False, primary_key=True)
    type_name = db.Column(db.String, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)

    # def __repr__(self):
    #     return '<Likeable %r>' % self.value