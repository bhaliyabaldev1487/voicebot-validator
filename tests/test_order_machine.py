import json

from validators.order_validator import OrderValidator


def test_order_flow():

    with open(
        "tests/sample_order_transcript.json"
    ) as fp:

        transcript = json.load(fp)

    result = OrderValidator().validate(
        transcript["segments"]
    )

    assert (
        result["final_state"]
        ==
        "IDENTIFIER_RECEIVED"
    )
