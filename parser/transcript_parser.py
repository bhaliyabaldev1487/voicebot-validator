import json


class TranscriptParser:

    def load(self, file_path):

        with open(file_path) as fp:

            return json.load(fp)

    def segments(self, transcript):

        return transcript["segments"]
