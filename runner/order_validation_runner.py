from __future__ import annotations

"""
runner/order_validation_runner.py

High-level orchestration for validating one order-flow conversation.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from database.mysql_provider import MySQLDatabaseProvider
from extractors.bot_response_extractor import BotResponseExtractor
from extractors.order_entities_extractor import OrderEntitiesExtractor
from models.lookup import OrderLookupRequest
from models.validation_context import ValidationContext
from parser.transcript_parser import TranscriptParser
from reporting.html_reporter import HTMLReporter
from reporting.json_reporter import JSONReporter
from services.order_lookup_service import OrderLookupService
from validators.order_flow_validator import OrderFlowValidator
from validators.response_validator import ResponseValidator


class OrderValidationRunner:
    """
    End-to-end order validation pipeline.
    """

    def __init__(
        self,
        db_connection_url: Optional[str] = None,
        db_echo: bool = False,
        db_provider=None,
        lookup_service=None,
    ) -> None:

        self.db_connection_url = db_connection_url
        self.db_echo = db_echo
        self._db_provider = db_provider
        self._lookup_service = lookup_service

        self.transcript_parser = TranscriptParser()
        self.entities_extractor = OrderEntitiesExtractor()
        self.bot_response_extractor = BotResponseExtractor()

        self.validator = OrderFlowValidator()
        self.response_validator = ResponseValidator()

    def run(
        self,
        transcript_file: str,
        caller_phone: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        # --------------------------------------------------
        # Parse transcript
        # --------------------------------------------------

        transcript = self.transcript_parser.parse_file(transcript_file)

        entities = self.entities_extractor.extract(
            transcript.customer_text
        )

        bot_response = self.bot_response_extractor.extract(
            transcript
        )

        # --------------------------------------------------
        # Database
        # --------------------------------------------------

        db = self._db_provider or MySQLDatabaseProvider(
            connection_url=self.db_connection_url,
            echo=self.db_echo,
        )

        lookup_service = (
            self._lookup_service
            or OrderLookupService(db)
        )

        lookup_result = lookup_service.lookup(
            OrderLookupRequest(
                caller_phone=caller_phone,
                order_number=entities.order_number,
                customer_phone=entities.customer_phone,
                customer_mobile=entities.customer_mobile,
                customer_email=entities.customer_email,
            )
        )

        # --------------------------------------------------
        # Debug Output
        # --------------------------------------------------

        print("\n========== DATABASE LOOKUP ==========")

        print("\nCustomer")

        if lookup_result.customer:
            print(vars(lookup_result.customer))
        else:
            print("Not Found")

        print("\nOrder")

        if lookup_result.order:
            print(vars(lookup_result.order))
        else:
            print("Not Found")

        print("\n=====================================")

        # --------------------------------------------------
        # Validation Context
        # --------------------------------------------------

        # context = ValidationContext(
        #     transcript=transcript,
        #     entities=entities,
        #     lookup_result=lookup_result,
        #     caller_phone=caller_phone,
        #     conversation_id=conversation_id,
        # )
        context = ValidationContext(
            transcript=transcript,
            entities=entities,
            lookup_result=lookup_result,
            bot_response=bot_response,
            caller_phone=caller_phone,
            conversation_id=conversation_id,
        )
        #
        # Temporary until ConversationContext is introduced
        #
        context.bot_response = bot_response

        # --------------------------------------------------
        # Existing Validation
        # --------------------------------------------------

        validation_result = self.validator.validate(context)

        response_validation = self.response_validator.validate(context)

        return{
        "conversation_id": conversation_id,
        "caller_phone": caller_phone,
        "transcript_file": transcript_file,
        "entities": entities.to_dict(),
        "lookup": lookup_result.to_dict(),
        "bot_response": bot_response.to_dict(),
        "validation": validation_result.to_dict(),
        "response_validation": [
            item.to_dict() for item in response_validation
        ],
    }

    def run_and_write_reports(
        self,
        transcript_file: str,
        caller_phone: Optional[str] = None,
        conversation_id: Optional[str] = None,
        output_dir: str = "reports",
    ) -> Dict[str, Any]:

        result = self.run(
            transcript_file=transcript_file,
            caller_phone=caller_phone,
            conversation_id=conversation_id,
        )

        output_path = Path(output_dir)
        output_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        base_name = (
            conversation_id
            or Path(transcript_file).stem
        )

        json_file = output_path / f"{base_name}.json"
        html_file = output_path / f"{base_name}.html"

        JSONReporter().write(
            result,
            str(json_file),
        )

        HTMLReporter().write(
            result,
            str(html_file),
        )

        result["report_files"] = {
            "json": str(json_file),
            "html": str(html_file),
        }

        return result