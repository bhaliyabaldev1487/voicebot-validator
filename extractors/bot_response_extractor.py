import re

from models.bot_response import BotOrderResponse


class BotResponseExtractor:

    ORDER_PATTERN = re.compile(r"(AZA[0-9]+)", re.I)

    TRACKING_PATTERN = re.compile(r"\b([A-Z]{2,5}[0-9]{6,15})\b")

    STATUS = [
        "PROCESSING",
        "SHIPPING",
        "DELIVERED",
        "CANCELLED",
    ]

    PAYMENT = [
        "PAID",
        "SUCCESS",
        "FAILED",
        "PENDING",
    ]

    COURIERS = [
        "BlueDart",
        "Delhivery",
        "FedEx",
        "DHL",
        "Xpressbees",
        "Ecom",
    ]

    def extract(self, transcript):

        response = BotOrderResponse()

        # Your ParsedTranscript already provides this property
        bot_text = transcript.bot_text

        order = self.ORDER_PATTERN.search(bot_text)

        if order:
            response.order_number = order.group(1)

        for status in self.STATUS:
            
            if status.lower() in bot_text.lower():
                response.order_status = status
                break

        for courier in self.COURIERS:

            if courier.lower() in bot_text.lower():
                response.courier = courier
                break

        tracking = self.TRACKING_PATTERN.search(bot_text)

        if tracking:
            response.tracking_number = tracking.group(1)

        for payment in self.PAYMENT:

            if payment.lower() in bot_text.lower():
                response.payment_status = payment
                break

        return response