from __future__ import annotations

"""
runner/order_validation_runner.py

High-level orchestration for validating one order-flow conversation.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from database.mysql_provider import MySQLDatabaseProvider
from extractors.order_entities_extractor import OrderEntitiesExtractor
from models.lookup import OrderLookupRequest
from models.validation_context import ValidationContext
from parser.transcript_parser import TranscriptParser
from reporting.html_reporter import HTMLReporter
from reporting.json_reporter import JSONReporter
from services.order_lookup_service import OrderLookupService
from validators.order_flow_validator import OrderFlowValidator
from extractors.bot_response_extractor import BotResponseExtractor
from services.comparison_service import ComparisonService

class OrderValidationRunner:
    """
    Orchestrates the complete order-flow validation pipeline:
    1. Parse transcript
    2. Extract entities
    3. Lookup customer/order from DB
    4. Validate bot response against DB data
    5. Return result and optionally write reports
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
        self.validator = OrderFlowValidator()

    def run(
        self,
        transcript_file: str,
        caller_phone: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute one end-to-end validation run.
        """
        transcript = self.transcript_parser.parse_file(transcript_file)
        entities = self.entities_extractor.extract(transcript.customer_text)

        db = self._db_provider or MySQLDatabaseProvider(
            connection_url=self.db_connection_url,
            echo=self.db_echo,
        )

        lookup_service = self._lookup_service or OrderLookupService(db)

        lookup_result = lookup_service.lookup(
            OrderLookupRequest(
                caller_phone=caller_phone,
                order_number=entities.order_number,
                customer_phone=entities.customer_phone,
                customer_mobile=entities.customer_mobile,
                customer_email=entities.customer_email,
            )
        )
        print("\n========== DATABASE LOOKUP ==========")

        print("Customer:")
        if lookup_result.customer:
            print(vars(lookup_result.customer))
        else:
            print("Not Found")

        print("\nOrder:")
        if lookup_result.order:
            print(vars(lookup_result.order))
        else:
            print("Not Found")

        print("=====================================\n")

        context = ValidationContext(
            transcript=transcript,
            entities=entities,
            lookup_result=lookup_result,
            caller_phone=caller_phone,
            conversation_id=conversation_id,
        )

        validation_result = self.validator.validate(context)

        bot_response = BotResponseExtractor().extract(transcript)

        comparison = ComparisonService().compare(
            lookup_result.order,
            bot_response,
        )

        return {
            "conversation_id": conversation_id,
            "caller_phone": caller_phone,
            "bot_response": bot_response.to_dict(),
            "comparison": [x.to_dict() for x in comparison],
            "validation": validation_result.to_dict(),
        }
    
        # return {
        #     "conversation_id": conversation_id,
        #     "caller_phone": caller_phone,
        #     "transcript_file": transcript_file,
        #     "entities": entities.to_dict() if hasattr(entities, "to_dict") else vars(entities),
        #     "lookup": lookup_result.to_dict() if hasattr(lookup_result, "to_dict") else vars(lookup_result),
        #     "validation": (
        #         validation_result.to_dict()
        #         if hasattr(validation_result, "to_dict")
        #         else vars(validation_result)
        #     ),
        # }

    def run_and_write_reports(
        self,
        transcript_file: str,
        caller_phone: Optional[str] = None,
        conversation_id: Optional[str] = None,
        output_dir: str = "reports",
    ) -> Dict[str, Any]:
        """
        Run validation and write JSON + HTML reports.
        """
        result = self.run(
            transcript_file=transcript_file,
            caller_phone=caller_phone,
            conversation_id=conversation_id,
        )

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        base_name = conversation_id or Path(transcript_file).stem
        json_file = output_path / f"{base_name}.json"
        html_file = output_path / f"{base_name}.html"

        JSONReporter().write(result, str(json_file))
        HTMLReporter().write(result, str(html_file))

        result["report_files"] = {
            "json": str(json_file),
            "html": str(html_file),
        }

        return result