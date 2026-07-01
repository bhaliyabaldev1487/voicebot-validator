from state_machine.machine import StateMachine
from state_machine.state import ConversationState

from extractors.intent_extractor import IntentExtractor
from extractors.entity_extractor import EntityExtractor


class OrderConversationMachine:

    def __init__(self):

        self.machine = StateMachine()

        self.intent = IntentExtractor()

        self.entities = EntityExtractor()

    def process(self, conversation):

        for segment in conversation:

            speaker = segment["speaker"]

            text = segment["text"]

            state = self.machine.state()

            if (
                state == ConversationState.START
                and
                speaker == "CUSTOMER"
            ):

                if self.intent.detect(text) == "ORDER":

                    self.machine.move(
                        ConversationState.ORDER_INTENT_DETECTED
                    )

            elif (
                state == ConversationState.ORDER_INTENT_DETECTED
                and
                speaker == "BOT"
            ):

                self.machine.move(
                    ConversationState.WAITING_FOR_IDENTIFIER
                )

            elif (
                state == ConversationState.WAITING_FOR_IDENTIFIER
                and
                speaker == "CUSTOMER"
            ):

                if (

                    self.entities.order_number(text)

                    or

                    self.entities.phone(text)

                    or

                    self.entities.email(text)

                ):

                    self.machine.move(
                        ConversationState.IDENTIFIER_RECEIVED
                    )

        return self.machine
