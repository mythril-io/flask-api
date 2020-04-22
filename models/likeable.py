from extensions import db
from datetime import datetime
from sqlalchemy import event, and_
from sqlalchemy.orm import relationship, foreign, remote, backref, column_property
from sqlalchemy import select, func

__all__ = ['Likeable']

class HasLikes():
    pass

class Likeable(db.Model):
    __tablename__ = 'likeables'
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, primary_key=True)
    likeable_id = db.Column(db.Integer, nullable=False, primary_key=True)
    likeable_type = db.Column(db.String, nullable=False)
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
                                        Likeable.likeable_type == type
                                    ),
                        backref=backref(
                                'parent_{}'.format(type),
                                primaryjoin=remote(class_.id) == foreign(Likeable.likeable_id)
                                )
                        )

    class_.likes = column_property(
        select([func.count('*')]).where(and_(
                Likeable.likeable_id == class_.id,
                Likeable.value == 1, 
            )).correlate_except(Likeable)
    )

    class_.dislikes = column_property(
        select([func.count('*')]).where(and_(
                Likeable.likeable_id == class_.id,
                Likeable.value == 0, 
            )).correlate_except(Likeable)
    )

    @event.listens_for(class_.likeables, 'append')
    def append_like(target, value, initiator):
        value.likeable_type = type