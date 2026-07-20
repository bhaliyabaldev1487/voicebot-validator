from collections import OrderedDict

from models.speaker_profile import SpeakerProfile


class SpeakerProfileBuilder:

    def build(self, segments):

        profiles = OrderedDict()

        for seg in segments:

            speaker = (
                seg.get("speaker")
                or seg.get("speaker_label")
                or seg.get("role")
            )

            if not speaker:
                continue

            speaker = speaker.lower()

            if speaker not in profiles:
                profiles[speaker] = SpeakerProfile(
                    speaker=speaker
                )

            profiles[speaker].add(
                seg.get("text", "")
            )

        return list(profiles.values())