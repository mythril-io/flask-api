import flask_praetorian
from extensions import db
from sqlalchemy import or_, and_

from models import Likeable

class Likeables():
    def like(self, likeable_id, likeable_name, value):
        """
        Like/Dislike a model
        """

        # Fetch likeable
        current_user = flask_praetorian.current_user()
        likeable = Likeable.query.filter_by(and_(
                Likeable.user_id == current_user.id, 
                Likeable.likeable_id == likeable_id
            )).first()

        if likeable is None:
            # Create new Likeable
            new_likeable = Likeable(
                user_id = current_user.id,
                likeable_id = likeable_id,
                likeable_name = likeable_name,
                value = value
            )
            try:
                db.session.add(new_likeable)
                db.session.commit()
            except Exception:
                return 500

        elif likeable.value != value:
            # Update Likeable
            likeable.value = value
            try:
                db.session.commit()
            except Exception:
                return 500

        else:
            # Remove Likeable
            return self.remove(likeable_id)

        return 200

    def remove(self, likeable_id):
        """
        Remove a Likeable entry
        """

        # Fetch likeable
        current_user = flask_praetorian.current_user()
        like = Likeable.query.filter_by(and_(
                Likeable.user_id == current_user.id, 
                Likeable.likeable_id == likeable_id
            )).first()

        if like is None:
            return 404

        try:
            db.session.delete(like)
            db.session.commit()
        except Exception:
            return 500

        return 200

    # def dislike(self, likeable_id, likeable_name):
    #     """
    #     Dislike a model
    #     """

    #     current_user = flask_praetorian.current_user()