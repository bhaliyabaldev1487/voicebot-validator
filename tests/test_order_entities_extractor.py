from extractors.order_entities_extractor import OrderEntitiesExtractor


def test_extract_order_number_email_phone():
    text = """
    Hi, I want to check my order status.
    My order number is AZA12345.
    My email is baldev@example.com
    and my mobile number is 9876543210.
    """

    extractor = OrderEntitiesExtractor()
    entities = extractor.extract(text)

    assert entities.order_number == "AZA12345"
    assert entities.customer_email == "baldev@example.com"
    assert entities.customer_phone == "9876543210" or entities.customer_mobile == "9876543210"


def test_extract_when_only_email_present():
    text = "I want to know my order details. My email is testuser@gmail.com"

    extractor = OrderEntitiesExtractor()
    entities = extractor.extract(text)

    assert entities.customer_email == "testuser@gmail.com"
    assert entities.order_number is None