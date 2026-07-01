from state_machine.transitions import ALLOWED_TRANSITIONS
from state_machine.state import ConversationState


class StateMachine:

    def __init__(self):

        self.current = ConversationState.START

        self.history = []

    def move(self, next_state):

        allowed = ALLOWED_TRANSITIONS.get(
            self.current.value,
            []
        )

        if next_state.value not in allowed:

            raise Exception(
                f"Invalid Transition "
                f"{self.current} -> {next_state}"
            )

        self.history.append(
            (
                self.current,
                next_state
            )
        )

        self.current = next_state

    def state(self):

        return self.current
