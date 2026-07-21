from classifiers import (
    SpeakerProfileBuilder,
    BotClassifier,
    CustomerClassifier,
    ConversationClassifier,
)

segments = [
    {"speaker": "SPEAKER_00", "text": "Hello, welcome to Aza Fashions."},
    {"speaker": "SPEAKER_00", "text": "How can I help you today?"},
    {"speaker": "SPEAKER_03", "text": "My order number is UOYSTD77."},
    {"speaker": "SPEAKER_03", "text": "Where is my order?"},
]

builder = SpeakerProfileBuilder()
profiles = builder.build(segments)

bot = BotClassifier()
customer = CustomerClassifier()

for profile in profiles.values():
    bot.score(profile)
    customer.score(profile)

ConversationClassifier().score(profiles)

for profile in profiles.values():
    print(profile.to_dict())