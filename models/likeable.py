from extensions import db
from datetime import datetime
from sqlalchemy import event, and_
from sqlalchemy.orm import relationship, foreign, remote, backref

__all__ = ['Likeable']

class HasLikes():
    pass

class Likeable(db.Model):
    __tablename__ = 'likeables'
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, primary_key=True)
    likeable_id = db.Column(db.Integer, nullable=False, primary_key=True)
    likeable_name = db.Column(db.String, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User')

    # def __repr__(self):
    #     return '<Likeable %r>' % self.value

@event.listens_for(HasLikes, 'mapper_configured', propagate=True)
def setup_listener(mapper, class_):
    name = class_.__name__
    type = name.lower()
    class_.likeables = relationship('Likeable',
                        primaryjoin=and_(
                                        class_.id == foreign(remote(Likeable.likeable_id)),
                                        Likeable.likeable_name == type
                                    ),
                        backref=backref(
                                'parent_{}'.format(type),
                                primaryjoin=remote(class_.id) == foreign(Likeable.likeable_id)
                                )
                        )
    @event.listens_for(class_.likeables, 'append')
    def append_like(target, value, initiator):
        value.likeable_name = type