from decimal import Decimal
from pathlib import Path
import json

from extractors.order_entities_extractor import OrderEntities
from models.customer import Customer
from models.lookup import LookupResult
from models.order import Order
from models.transcript import ParsedTranscript, TranscriptTurn
from models.validation_context import ValidationContext
from validators.order_flow_validator import OrderFlowValidator


def test_fixture_file_exists():
    fixture = Path("tests/fixtures/order_success_transcript.json")
    assert fixture.exists()


def test_fixture_json_loads():
    fixture = Path("tests/fixtures/order_success_transcript.json")
    payload = json.loads(fixture.read_text(encoding="utf-8"))

    assert "turns" in payload
    assert len(payload["turns"]) >= 2