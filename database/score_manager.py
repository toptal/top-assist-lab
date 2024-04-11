from models.user_score import UserScore
from slack.client import get_bot_user_id


class ScoreManager:
    def __init__(self, session):
        self.session = session
        self.bot_user_id = get_bot_user_id()

    def add_or_update_score(self, slack_user_id, category, points=1):
        """
        Adds or updates the score for a user in a given category. If the user does not exist, creates a new record.
        """
        if slack_user_id == self.bot_user_id:
            print("Skipping score update for bot user.")
            return
        user_score = self.session.query(UserScore).filter_by(slack_user_id=slack_user_id).first()
        if not user_score:
            user_score = UserScore(slack_user_id=slack_user_id)
            self.session.add(user_score)
            self.session.flush()  # Flush here to ensure user_score is persisted before we try to update it

        if category == 'seeker':
            user_score.seeker_score += points
        elif category == 'revealer':
            user_score.revealer_score += points
        elif category == 'luminary':
            user_score.luminary_score += points
        else:
            raise ValueError("Invalid category provided.")
        self.session.commit()

    def get_top_users(self, category, top_n=10):
        """
        Retrieves the top N users for a given category.
        """
        if category == 'seeker':
            return self.session.query(UserScore).order_by(UserScore.seeker_score.desc()).limit(top_n).all()
        elif category == 'revealer':
            return self.session.query(UserScore).order_by(UserScore.revealer_score.desc()).limit(top_n).all()
        elif category == 'luminary':
            return self.session.query(UserScore).order_by(UserScore.luminary_score.desc()).limit(top_n).all()
        else:
            raise ValueError("Invalid category provided.")
