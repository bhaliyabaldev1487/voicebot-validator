from decimal import Decimal

from extractors.order_entities_extractor import OrderEntities
from models.customer import Customer
from models.lookup import LookupResult
from models.order import Order
from models.transcript import ParsedTranscript, TranscriptTurn
from models.validation_context import ValidationContext
from validators.order_flow_validator import OrderFlowValidator


def build_order(
    order_number: str = "AZA12345",
    status: str = "SHIPPING",
    total_price: str = "5499.00",
) -> Order:
    return Order(
        order_id=1,
        customer_order_number=order_number,
        site_user_id=101,
        order_status=status,
        payment_status="PAID",
        total_price=Decimal(total_price),
        date_added=None,
    )


def build_customer() -> Customer:
    return Customer(
        site_user_id=101,
        first_name="Baldev",
        last_name="Bhaliya",
        email="baldev@example.com",
        phone_no="9876543210",
        mobile="9876543210",
    )


def build_transcript(customer_text: str, bot_text: str) -> ParsedTranscript:
    return ParsedTranscript(
        turns=[
            TranscriptTurn(speaker="customer", text=customer_text),
            TranscriptTurn(speaker="bot", text=bot_text),
        ],
        customer_text=customer_text,
        bot_text=bot_text,
        full_text=f"{customer_text}\n{bot_text}",
    )


def test_validator_passes_when_status_and_price_match():
    transcript = build_transcript(
        customer_text="I want to know my order status for AZA12345",
        bot_text="Your order AZA12345 is shipped and the total amount is 5499.00",
    )

    entities = OrderEntities(
        order_number="AZA12345",
        customer_email=None,
        customer_phone="9876543210",
        customer_mobile="9876543210",
        intent="order",
    )

    lookup = LookupResult(
        success=True,
        customer=build_customer(),
        order=build_order(status="SHIPPING", total_price="5499.00"),
        lookup_method="caller_phone -> order_number",
        message="Customer and order identified successfully.",
    )

    context = ValidationContext(
        transcript=transcript,
        entities=entities,
        lookup_result=lookup,
        caller_phone="9876543210",
    )

    result = OrderFlowValidator().validate(context)

    assert result.success is True
    assert result.failed_checks == 0


def test_validator_fails_when_status_mismatch():
    transcript = build_transcript(
        customer_text="I want to know my order status for AZA12345",
        bot_text="Your order AZA12345 is delivered and the total amount is 5499.00",
    )

    entities = OrderEntities(
        order_number="AZA12345",
        customer_email=None,
        customer_phone="9876543210",
        customer_mobile="9876543210",
        intent="order",
    )

    lookup = LookupResult(
        success=True,
        customer=build_customer(),
        order=build_order(status="SHIPPING", total_price="5499.00"),
        lookup_method="caller_phone -> order_number",
        message="Customer and order identified successfully.",
    )

    context = ValidationContext(
        transcript=transcript,
        entities=entities,
        lookup_result=lookup,
        caller_phone="9876543210",
    )

    result = OrderFlowValidator().validate(context)

    assert result.success is False
    failed_names = [c.name for c in result.checks if not c.passed]
    assert "order_status_match" in failed_names