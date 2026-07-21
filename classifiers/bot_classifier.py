from models.speaker_profile import SpeakerProfile


class BotClassifier:

    def score(self, profile: SpeakerProfile) -> float:

        score = 0.0

        score += profile.greeting_count * 5
        score += profile.help_count * 5
        score += profile.language_selection_count * 4

        if profile.average_length > 8:
            score += 3

        if profile.question_count == 0:
            score += 2

        if profile.order_mentions > 0:
            score += 2

        profile.bot_score = score

        return score