from extensions import db
from datetime import datetime

__all__ = ['User']

user_role = db.Table('user_role',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    extend_existing=True
)

user_following = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('leader_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    extend_existing=True
)

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    is_verified = db.Column(db.Integer, default=0)
    roles = db.relationship('Role', secondary=user_role, lazy='subquery',
        backref=db.backref('users', lazy=False))
    about_me = db.Column(db.Text, unique=False, nullable=True)
    avatar = db.Column(db.String, unique=False, nullable=True)
    banner = db.Column(db.String, unique=False, nullable=True)
    timezone = db.Column(db.String, unique=False, nullable=True)
    birthday = db.Column(db.Date, unique=False, nullable=True)
    gender = db.Column(db.String, unique=False, nullable=True)
    location = db.Column(db.String, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    following = db.relationship(
        'User', lambda: user_following,
        primaryjoin=lambda: User.id == user_following.c.follower_id,
        secondaryjoin=lambda: User.id == user_following.c.leader_id,
        backref='followers'
    )

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def rolenames(self):
        try:
            role_names = []
            for role in self.roles:
                role_names.append(role.name)
            return role_names
            # return self.roles.split(',')
        except Exception:
            return []

    @rolenames.setter
    def rolenames(self, rolenames):
        self._rolenames = rolenames

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id

    # twitter = db.Column(db.String, unique=False, nullable=True)
    # facebook = db.Column(db.String, unique=False, nullable=True)
    # instagram = db.Column(db.String, unique=False, nullable=True)
    # discord = db.Column(db.String, unique=False, nullable=True)
    # youtube = db.Column(db.String, unique=False, nullable=True)
    # twitch = db.Column(db.String, unique=False, nullable=True)
    # deviant_art = db.Column(db.String, unique=False, nullable=True)
    # reddit = db.Column(db.String, unique=False, nullable=True)
    # patreon = db.Column(db.String, unique=False, nullable=True)
    # tumblr = db.Column(db.String, unique=False, nullable=True)
    # battle_net = db.Column(db.String, unique=False, nullable=True)
    # steam = db.Column(db.String, unique=False, nullable=True)
    # playstation = db.Column(db.String, unique=False, nullable=True)
    # nintendo_switch = db.Column(db.String, unique=False, nullable=True)
    # xbox = db.Column(db.String, unique=False, nullable=True)