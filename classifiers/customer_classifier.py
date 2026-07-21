from models.speaker_profile import SpeakerProfile


class CustomerClassifier:

    def score(self, profile: SpeakerProfile) -> float:

        score = 0.0

        score += profile.question_count * 5

        score += profile.order_mentions * 3

        score += profile.refund_mentions * 3

        score += profile.email_mentions * 2

        score += profile.phone_mentions * 2

        if profile.average_length < 15:
            score += 1

        profile.customer_score = score

        return score