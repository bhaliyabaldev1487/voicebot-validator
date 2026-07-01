BOT_ACTIONS = {

    "REQUEST_ORDER_NUMBER": [

        "order number",

        "order id"

    ],

    "REQUEST_PHONE": [

        "registered mobile",

        "phone number"

    ],

    "REQUEST_EMAIL": [

        "email address",

        "registered email"

    ]

}


class BotActionExtractor:

    def detect(self, text):

        text = text.lower()

        for action, phrases in BOT_ACTIONS.items():

            for phrase in phrases:

                if phrase in text:

                    return action

        return None
