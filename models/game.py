from extensions import db
from datetime import datetime

__all__ = ['Game']

game_genre = db.Table('game_genre',
    db.Column('game_id', db.Integer, db.ForeignKey('games.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True),
    extend_existing=True
)

class Game(db.Model):
    __tablename__ = 'games'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    slug = db.Column(db.String, unique=True, nullable=False)
    synopsis = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String, unique=True, nullable=False)
    banner = db.Column(db.String, unique=True, nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey('developers.id'), nullable=False)
    score = db.Column(db.Float, nullable=True)
    library_count = db.Column(db.Integer, nullable=True)
    score_rank = db.Column(db.Integer, nullable=True)
    popularity_rank = db.Column(db.Integer, nullable=True)
    trending_page_views = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    releases = db.relationship('Release', backref='games', cascade="all")
    genres = db.relationship('Genre', secondary=game_genre, backref=db.backref('games'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = db.relationship('User')

    def __repr__(self):
        return '<Game %r>' % self.title

    @classmethod
    def lookup(cls, title):
        return cls.query.filter_by(title=title).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)