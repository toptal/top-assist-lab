from models.user_score import UserScore
from slack.client import get_bot_user_id
from database.database import get_db_session


class ScoreManager:
    def __init__(self):
        self.bot_user_id = get_bot_user_id()

    def add_or_update_score(self, slack_user_id, category, points=1):
        """
        Adds or updates the score for a user in a given category. If the user does not exist, creates a new record.
        """
        if slack_user_id == self.bot_user_id:
            print("Skipping score update for bot user.")
            return
        with get_db_session() as session:
            user_score = session.query(UserScore).filter_by(slack_user_id=slack_user_id).first()
            if not user_score:
                user_score = UserScore(slack_user_id=slack_user_id)
                session.add(user_score)
                session.flush()  # Flush here to ensure user_score is persisted before we try to update it

            if category == 'seeker':
                user_score.seeker_score += points
            elif category == 'revealer':
                user_score.revealer_score += points
            elif category == 'luminary':
                user_score.luminary_score += points
            else:
                raise ValueError("Invalid category provided.")

    def get_top_users(self, category, top_n=10):
        """
        Retrieves the top N users for a given category.
        """
        with get_db_session() as session:
            if category == 'seeker':
                return session.query(UserScore).order_by(UserScore.seeker_score.desc()).limit(top_n).all()
            elif category == 'revealer':
                return session.query(UserScore).order_by(UserScore.revealer_score.desc()).limit(top_n).all()
            elif category == 'luminary':
                return session.query(UserScore).order_by(UserScore.luminary_score.desc()).limit(top_n).all()
            else:
                raise ValueError("Invalid category provided.")
