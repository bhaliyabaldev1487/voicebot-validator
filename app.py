from parser.transcript_parser import TranscriptParser

from database.mysql_adapter import MySQLAdapter

print("=" * 50)
print("VoiceBot Validator")
print("=" * 50)

parser = TranscriptParser()

transcript = parser.load(
    "transcript/sample.json"
)

print(len(transcript["segments"]))

db = MySQLAdapter()

print("Database Connected")
