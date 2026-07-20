from classifiers.bot_classifier import BotClassifier
from classifiers.customer_classifier import CustomerClassifier
from classifiers.speaker_profile_builder import SpeakerProfileBuilder
from models.speaker_role_resolution import SpeakerRoleResolution

class SpeakerRoleResolver:

    def __init__(self):

        self.builder = SpeakerProfileBuilder()

        self.bot_classifier = BotClassifier()

        self.customer_classifier = CustomerClassifier()

    def resolve(self, segments):

        profiles = self.builder.build(segments)

        mapping = {}

        print("\n========== SPEAKER PROFILES ==========\n")

        for profile in profiles:
            profile.bot_score = self.bot_classifier.score(profile)
            profile.customer_score = self.customer_classifier.score(profile)
            profile.decide_role()
            mapping[profile.speaker] = profile.role
            print(profile.to_dict())
            print()
        print("======================================\n")

        return SpeakerRoleResolution(
            mapping=mapping
        )