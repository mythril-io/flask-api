from extensions import db
from sqlalchemy import or_, and_

from models import Likeable

class Likeables():
    def create(self, user_id, likeable_type, likeable_id, value):
        """
        Like/Dislike a model
        """
        # Fetch likeable
        likeable = Likeable.query.filter(and_(
                Likeable.user_id == user_id, 
                Likeable.likeable_type == likeable_type,
                Likeable.likeable_id == likeable_id,
            )).first()

        if likeable is None:
            # Create new Likeable
            new_likeable = Likeable(
                user_id = user_id,
                likeable_type = likeable_type,
                likeable_id = likeable_id,
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
            return self.remove(self, user_id, likeable_type, likeable_id)

        return 200

    def remove(self, user_id, likeable_type, likeable_id):
        """
        Remove a Likeable entry
        """
        # Fetch likeable
        likeable = Likeable.query.filter(and_(
                Likeable.user_id == user_id, 
                Likeable.likeable_type == likeable_type,
                Likeable.likeable_id == likeable_id
            )).first()

        if likeable is None:
            return 404

        try:
            db.session.delete(likeable)
            db.session.commit()
        except Exception:
            return 500

        return 200

    def getCount(self, likeable_type, likeable_id):
        """
        Get Like/Dislike count for specified Likeable id
        """
        like_count = Likeable.query.filter(and_(
                Likeable.likeable_id == likeable_id,
                Likeable.likeable_type == likeable_type,
                Likeable.value == 1, 
            )).count()

        dislike_count = Likeable.query.filter(and_(
                Likeable.likeable_id == likeable_id,
                Likeable.likeable_type == likeable_type,
                Likeable.value == 0, 
            )).count()

        response = {
            'like_count': like_count,
            'dislike_count': dislike_count,
        }

        return response

    def getUserSentiment(self, user_id, likeable_type, likeable_id):
        """
        Get User Sentiment by Likeable id
        """

        likeable = Likeable.query.filter(and_(
                Likeable.user_id == user_id,
                Likeable.likeable_type == likeable_type,
                Likeable.likeable_id == likeable_id,
            )).first()

        user_sentiment = None if likeable == None else likeable.value

        return { 'user_sentiment': user_sentiment }