"""
Base interface for all validation rules.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.validation_context import ValidationContext
from models.validation_evidence import ValidationEvidence


class ValidationRule(ABC):

    @abstractmethod
    def validate(
        self,
        context: ValidationContext,
    ) -> ValidationEvidence:
        """
        Validate one rule.

        Returns one ValidationEvidence.
        """
        raise NotImplementedError