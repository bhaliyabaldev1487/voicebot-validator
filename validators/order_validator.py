from state_machine.order_machine import OrderConversationMachine


class OrderValidator:

    def validate(self, transcript):

        machine = OrderConversationMachine()

        machine.process(transcript)

        return {

            "final_state": machine.state().value,

            "history": [

                {

                    "from": x.value,

                    "to": y.value

                }

                for x, y in machine.history

            ]

        }
