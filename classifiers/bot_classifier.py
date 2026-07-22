from __future__ import annotations

from models.speaker_profile import SpeakerProfile


class BotClassifier:

    BOT_PHRASES = [

        "hello",

        "welcome",

        "thank you for calling",

        "how can i help",

        "how may i help",

        "anything else i can help",

        "please hold",

        "please wait",

        "one moment",

        "english or arabic",

        "please let me know",

        "are you still there",

        "thank you",

        "goodbye",

        "have a great day",

        "please share your order number",

        "can you confirm",

    ]

    def score(
        self,
        profile: SpeakerProfile,
    ) -> float:

        score = 0.0

        score += profile.greeting_count * 4

        score += profile.help_count * 5

        score += profile.language_selection_count * 5

        score += profile.script_repetition * 6

        text = profile.conversation_text.lower()

        for phrase in self.BOT_PHRASES:

            if phrase in text:

                score += 5

        if profile.avg_words_per_turn > 10:

            score += 3

        if profile.question_ratio < 0.30:

            score += 2

        if "your order" in text:

            score += 3

        if "thank you for calling" in text:

            score += 8

        if "anything else" in text:

            score += 5

        profile.bot_score = score

        return score