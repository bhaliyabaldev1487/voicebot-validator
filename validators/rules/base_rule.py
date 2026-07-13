from abc import ABC, abstractmethod

from models.conversation_context import ConversationContext
from models.validation_evidence import ValidationEvidence


class ValidationRule(ABC):
    """
    Base interface for all validation rules.
    """

    @abstractmethod
    def validate(
        self,
        context: ConversationContext,
    ) -> ValidationEvidence:
        """
        Execute validation and return one evidence object.
        """
        pass