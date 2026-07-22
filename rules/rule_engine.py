"""
rules/rule_engine.py

Generic semantic rule engine.

This engine is intentionally domain-independent.
Order, Payment, Shipment, Return etc. should inherit from this class.

Responsibilities
----------------
* Register rules
* Execute rules
* Rank matches
* Return SemanticResult
"""

from __future__ import annotations

import logging
from abc import ABC
from typing import Dict, Iterable, List, Optional

from models.semantic_match import (
    SemanticEvidence,
    SemanticResult,
    StatusMatch,
    StatusRule,
)

from rules.similarity_engine import SimilarityEngine
from rules.text_matcher import TextMatcher


logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Base Rule Engine
# ----------------------------------------------------------------------


class BaseRuleEngine(ABC):
    """
    Base semantic rule engine.

    Concrete engines should subclass this class.

    Example:

        class OrderRuleEngine(BaseRuleEngine):
            ...

        class PaymentRuleEngine(BaseRuleEngine):
            ...
    """

    DEFAULT_THRESHOLD = 0.80

    def __init__(
        self,
        rules: Optional[List[StatusRule]] = None,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> None:

        self.threshold = threshold

        self.matcher = TextMatcher()

        self.similarity = SimilarityEngine()

        self._rules: List[StatusRule] = []

        if rules:
            self.register_rules(rules)

    # ------------------------------------------------------------------
    # Rule Registration
    # ------------------------------------------------------------------

    def register_rule(
        self,
        rule: StatusRule,
    ) -> None:
        """
        Register one rule.
        """

        self._rules.append(rule)

        self._rules.sort(
            key=lambda r: r.priority,
            reverse=True,
        )

    # ------------------------------------------------------------------

    def register_rules(
        self,
        rules: Iterable[StatusRule],
    ) -> None:
        """
        Register multiple rules.
        """

        for rule in rules:
            self.register_rule(rule)

    # ------------------------------------------------------------------

    def clear_rules(self) -> None:
        """
        Remove all registered rules.
        """

        self._rules.clear()

    # ------------------------------------------------------------------

    @property
    def rules(self) -> List[StatusRule]:
        """
        Returns registered rules.
        """

        return list(self._rules)

    # ------------------------------------------------------------------

    @property
    def enabled_rules(self) -> List[StatusRule]:
        """
        Returns enabled rules only.
        """

        return [
            r
            for r in self._rules
            if r.enabled
        ]

    # ------------------------------------------------------------------

    def total_rules(self) -> int:

        return len(self._rules)

    # ------------------------------------------------------------------

    def has_rules(self) -> bool:

        return bool(self._rules)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        text: str,
    ) -> SemanticResult:
        """
        Main entry point.

        Returns SemanticResult.
        """

        result = SemanticResult(
            document=text,
        )

        if not text:
            return result

        if not self.has_rules():
            logger.warning(
                "No rules registered for %s",
                self.__class__.__name__,
            )
            return result

        normalized = self.matcher.normalize_document(
            text,
        )

        self._evaluate_document(
            normalized,
            result,
        )

        result.sort()

        return result

    # ------------------------------------------------------------------

    def evaluate_sentences(
        self,
        text: str,
    ) -> SemanticResult:
        """
        Evaluate sentence by sentence.
        """

        result = SemanticResult(
            document=text,
        )

        sentences = self.matcher.split_sentences(
            text,
        )

        for sentence in sentences:

            self._evaluate_document(
                sentence,
                result,
            )

        result.sort()

        return result

    # ------------------------------------------------------------------
    # Protected Hooks
    # ------------------------------------------------------------------

    def _evaluate_document(
        self,
        text: str,
        result: SemanticResult,
    ) -> None:
        """
        Implemented in Part-B.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------

    def _create_match(
        self,
        rule: StatusRule,
        confidence: float,
        phrase: Optional[str] = None,
        pattern: Optional[str] = None,
        sentence: Optional[str] = None,
        score: float = 0.0,
        negative: bool = False,
    ) -> StatusMatch:
        """
        Helper used by Part-B.
        """

        evidence = SemanticEvidence(

            matched_phrase=phrase,

            matched_pattern=pattern,

            sentence=sentence,

            confidence=confidence,

        )

        return StatusMatch(

            status=rule.canonical_status,

            confidence=confidence,

            evidence=evidence,

            rule=rule,

            score=score,

            is_negative_match=negative,

        )

    # ------------------------------------------------------------------

    def _best_similarity(
        self,
        text: str,
        candidates: Iterable[str],
    ):
        """
        Wrapper around SimilarityEngine.
        """

        return self.similarity.find_best_match(
            text,
            candidates,
        )

    # ------------------------------------------------------------------

    def _log_match(
        self,
        match: StatusMatch,
    ) -> None:

        logger.debug(
            "[%s] %.3f -> %s",
            match.status,
            match.confidence,
            match.evidence.matched_phrase,
        )

    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, object]:
        """
        Engine summary.
        """

        return {

            "engine": self.__class__.__name__,

            "rules": len(self._rules),

            "enabled": len(self.enabled_rules),

            "threshold": self.threshold,

        }

    # ------------------------------------------------------------------

    def __len__(self) -> int:

        return len(self._rules)

    # ------------------------------------------------------------------

    def __bool__(self) -> bool:

        return self.has_rules()
    
        # ------------------------------------------------------------------
    # Rule Evaluation
    # ------------------------------------------------------------------

    def _evaluate_document(
        self,
        text: str,
        result: SemanticResult,
    ) -> None:
        """
        Evaluate every enabled rule against the supplied text.
        """

        for rule in self.enabled_rules:

            match = self._evaluate_rule(
                text=text,
                rule=rule,
            )

            if match is None:
                continue

            if match.confidence < self.threshold:
                continue

            result.add(match)

            self._log_match(match)

    # ------------------------------------------------------------------

    def _evaluate_rule(
        self,
        text: str,
        rule: StatusRule,
    ) -> Optional[StatusMatch]:
        """
        Evaluate a single rule.

        Evaluation order

            1. Negative phrases
            2. Exact phrases
            3. Regex
            4. Semantic similarity
        """

        # ----------------------------------------------------------
        # Negative phrases
        # ----------------------------------------------------------

        negative = self._match_negative_phrase(
            text,
            rule,
        )

        if negative:
            return negative

        # ----------------------------------------------------------
        # Exact phrase
        # ----------------------------------------------------------

        exact = self._match_exact_phrase(
            text,
            rule,
        )

        if exact:
            return exact

        # ----------------------------------------------------------
        # Regex
        # ----------------------------------------------------------

        regex = self._match_regex(
            text,
            rule,
        )

        if regex:
            return regex

        # ----------------------------------------------------------
        # Similarity
        # ----------------------------------------------------------

        semantic = self._match_similarity(
            text,
            rule,
        )

        return semantic

    # ------------------------------------------------------------------
    # Negative Matching
    # ------------------------------------------------------------------

    def _match_negative_phrase(
        self,
        text: str,
        rule: StatusRule,
    ) -> Optional[StatusMatch]:

        if not rule.negative_phrases:
            return None

        phrase = self.matcher.find_matching_phrase(
            text,
            rule.negative_phrases,
        )

        if phrase is None:
            return None

        return self._create_match(
            rule=rule,
            confidence=1.0,
            phrase=phrase,
            sentence=text,
            score=1.0,
            negative=True,
        )

    # ------------------------------------------------------------------
    # Exact Matching
    # ------------------------------------------------------------------

    def _match_exact_phrase(
        self,
        text: str,
        rule: StatusRule,
    ) -> Optional[StatusMatch]:

        phrase = self.matcher.find_matching_phrase(
            text,
            rule.phrases,
        )

        if phrase is None:
            return None

        confidence = max(
            rule.confidence,
            self.matcher.confidence_from_match(
                len(phrase),
                len(text),
            ),
        )

        return self._create_match(
            rule=rule,
            confidence=confidence,
            phrase=phrase,
            sentence=text,
            score=confidence,
        )

    # ------------------------------------------------------------------
    # Regex Matching
    # ------------------------------------------------------------------

    def _match_regex(
        self,
        text: str,
        rule: StatusRule,
    ) -> Optional[StatusMatch]:

        if not rule.regex_patterns:
            return None

        for pattern in rule.regex_patterns:

            found = self.matcher.regex_search(
                text,
                pattern,
            )

            if found:

                matched = found.group(0)

                return self._create_match(
                    rule=rule,
                    confidence=rule.confidence,
                    phrase=matched,
                    pattern=pattern,
                    sentence=text,
                    score=rule.confidence,
                )

        return None

    # ------------------------------------------------------------------
    # Semantic Similarity
    # ------------------------------------------------------------------

    def _match_similarity(
        self,
        text: str,
        rule: StatusRule,
    ) -> Optional[StatusMatch]:

        if not rule.phrases:
            return None

        best = self._best_similarity(
            text,
            rule.phrases,
        )

        if best is None:
            return None

        if best.score < self.threshold:
            return None

        return self._create_match(
            rule=rule,
            confidence=best.score,
            phrase=best.target,
            sentence=text,
            score=best.score,
        )

    # ------------------------------------------------------------------
    # Multi Phrase Support
    # ------------------------------------------------------------------

    def _match_all_phrases(
        self,
        text: str,
        rule: StatusRule,
    ) -> List[StatusMatch]:

        matches: List[StatusMatch] = []

        for phrase in rule.phrases:

            if not self.matcher.contains_phrase(
                text,
                phrase,
            ):
                continue

            matches.append(

                self._create_match(
                    rule=rule,
                    confidence=rule.confidence,
                    phrase=phrase,
                    sentence=text,
                    score=rule.confidence,
                )

            )

        return matches

    # ------------------------------------------------------------------
    # Validation Helpers
    # ------------------------------------------------------------------

    def _passes_threshold(
        self,
        confidence: float,
    ) -> bool:

        return confidence >= self.threshold

    # ------------------------------------------------------------------

    @staticmethod
    def _highest_score(
        matches: List[StatusMatch],
    ) -> Optional[StatusMatch]:

        if not matches:
            return None

        return max(
            matches,
            key=lambda m: (
                m.confidence,
                m.score,
            ),
        )
    
        # ------------------------------------------------------------------
    # Result Aggregation
    # ------------------------------------------------------------------

    def _aggregate_matches(
        self,
        matches: List[StatusMatch],
    ) -> List[StatusMatch]:
        """
        Merge multiple matches for the same canonical status.

        Example

            "being stitched"
            "under processing"

        both become one PROCESSING match.
        """

        if not matches:
            return []

        grouped: Dict[str, List[StatusMatch]] = {}

        for match in matches:

            key = str(match.status)

            grouped.setdefault(
                key,
                []
            ).append(match)

        aggregated: List[StatusMatch] = []

        for status_matches in grouped.values():

            aggregated.append(
                self._merge_status_matches(
                    status_matches
                )
            )

        aggregated.sort(
            key=lambda m: (
                m.confidence,
                m.score,
            ),
            reverse=True,
        )

        return aggregated

    # ------------------------------------------------------------------

    def _merge_status_matches(
        self,
        matches: List[StatusMatch],
    ) -> StatusMatch:

        """
        Merge evidence belonging to one status.
        """

        if len(matches) == 1:
            return matches[0]

        best = max(
            matches,
            key=lambda m: (
                m.confidence,
                m.score,
            ),
        )

        phrases = []

        patterns = []

        confidence = best.confidence

        score = best.score

        for match in matches:

            evidence = match.evidence

            if evidence.matched_phrase:
                phrases.append(
                    evidence.matched_phrase
                )

            if evidence.matched_pattern:
                patterns.append(
                    evidence.matched_pattern
                )

            confidence = max(
                confidence,
                match.confidence,
            )

            score = max(
                score,
                match.score,
            )

        merged = self._create_match(

            rule=best.rule,

            confidence=confidence,

            phrase=", ".join(
                self.matcher.unique(phrases)
            ),

            pattern=", ".join(
                self.matcher.unique(patterns)
            ),

            sentence=best.evidence.sentence,

            score=score,

            negative=best.is_negative_match,

        )

        merged.evidence.metadata["match_count"] = len(matches)

        merged.evidence.metadata["phrases"] = phrases

        merged.evidence.metadata["patterns"] = patterns

        return merged

    # ------------------------------------------------------------------
    # Confidence Boosting
    # ------------------------------------------------------------------

    def _boost_confidence(
        self,
        match: StatusMatch,
    ) -> StatusMatch:
        """
        Increase confidence when multiple pieces of evidence exist.
        """

        metadata = match.evidence.metadata

        count = metadata.get(
            "match_count",
            1,
        )

        if count <= 1:
            return match

        bonus = min(
            0.02 * (count - 1),
            0.10,
        )

        match.confidence = min(
            1.0,
            match.confidence + bonus,
        )

        match.score = max(
            match.score,
            match.confidence,
        )

        metadata["confidence_bonus"] = round(
            bonus,
            3,
        )

        return match

    # ------------------------------------------------------------------
    # Duplicate Removal
    # ------------------------------------------------------------------

    def _remove_duplicate_matches(
        self,
        matches: List[StatusMatch],
    ) -> List[StatusMatch]:

        unique: Dict[str, StatusMatch] = {}

        for match in matches:

            key = (
                str(match.status),
                match.evidence.matched_phrase,
            )

            existing = unique.get(key)

            if existing is None:

                unique[key] = match

                continue

            if match.confidence > existing.confidence:

                unique[key] = match

        return list(
            unique.values()
        )

    # ------------------------------------------------------------------
    # Best Match Selection
    # ------------------------------------------------------------------

    def _select_best_match(
        self,
        matches: List[StatusMatch],
    ) -> Optional[StatusMatch]:

        if not matches:
            return None

        matches = self._aggregate_matches(
            matches
        )

        boosted = []

        for match in matches:

            boosted.append(
                self._boost_confidence(
                    match
                )
            )

        boosted.sort(

            key=lambda m: (

                m.confidence,

                m.score,

                m.rule.priority if m.rule else 0,

            ),

            reverse=True,

        )

        return boosted[0]

    # ------------------------------------------------------------------
    # Ranking
    # ------------------------------------------------------------------

    def _rank_matches(
        self,
        matches: List[StatusMatch],
    ) -> List[StatusMatch]:

        matches = self._remove_duplicate_matches(
            matches
        )

        matches = self._aggregate_matches(
            matches
        )

        ranked = []

        for match in matches:

            ranked.append(
                self._boost_confidence(
                    match
                )
            )

        ranked.sort(

            key=lambda m: (

                m.confidence,

                m.score,

                m.rule.priority if m.rule else 0,

            ),

            reverse=True,

        )

        return ranked
    
        # ------------------------------------------------------------------
    # Semantic Result Finalization
    # ------------------------------------------------------------------

    def finalize_result(
        self,
        result: SemanticResult,
    ) -> SemanticResult:
        """
        Finalize SemanticResult before returning to caller.

        Steps
        -----
        1. Remove negative matches
        2. Rank matches
        3. Update result
        """

        if not result.matches:
            return result

        positive_matches = [
            m
            for m in result.matches
            if not m.is_negative_match
        ]

        ranked = self._rank_matches(
            positive_matches
        )

        result.matches.clear()

        for match in ranked:
            result.add(match)

        result.sort()

        return result

    # ------------------------------------------------------------------
    # Public Search APIs
    # ------------------------------------------------------------------

    def find_best_match(
        self,
        text: str,
    ) -> Optional[StatusMatch]:
        """
        Return the highest ranked semantic match.
        """

        result = self.evaluate(text)

        result = self.finalize_result(result)

        return result.best_match

    # ------------------------------------------------------------------

    def find_all_matches(
        self,
        text: str,
    ) -> List[StatusMatch]:
        """
        Return every semantic match.
        """

        result = self.evaluate(text)

        result = self.finalize_result(result)

        return result.matches

    # ------------------------------------------------------------------

    def has_match(
        self,
        text: str,
    ) -> bool:

        return self.find_best_match(text) is not None

    # ------------------------------------------------------------------

    def match_status(
        self,
        text: str,
    ):

        match = self.find_best_match(text)

        if match is None:
            return None

        return match.status

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def explain(
        self,
        text: str,
    ) -> dict:
        """
        Returns a debug-friendly explanation.
        """

        result = self.evaluate(text)

        result = self.finalize_result(result)

        return {

            "engine": self.__class__.__name__,

            "rules_loaded": len(self.rules),

            "matches": [
                m.to_dict()
                for m in result.matches
            ],

            "best_match": (
                result.best_match.to_dict()
                if result.best_match
                else None
            ),

            "summary": self.summary(),

        }

    # ------------------------------------------------------------------

    def dump_rules(
        self,
    ) -> List[dict]:
        """
        Export rules for debugging.
        """

        output = []

        for rule in self.rules:

            output.append(
                rule.to_dict()
            )

        return output

    # ------------------------------------------------------------------
    # Extension Hooks
    # ------------------------------------------------------------------

    def before_evaluation(
        self,
        text: str,
    ) -> str:
        """
        Hook for subclasses.

        Example:
            normalize spoken numbers
            normalize order numbers
        """

        return text

    # ------------------------------------------------------------------

    def after_evaluation(
        self,
        result: SemanticResult,
    ) -> SemanticResult:
        """
        Hook for subclasses.

        Example:
            additional post-processing
        """

        return result

    # ------------------------------------------------------------------

    def evaluate_document(
        self,
        text: str,
    ) -> SemanticResult:
        """
        Enterprise evaluation pipeline.
        """

        text = self.before_evaluation(
            text,
        )

        result = self.evaluate(
            text,
        )

        result = self.finalize_result(
            result,
        )

        result = self.after_evaluation(
            result,
        )

        return result

    # ------------------------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(rules={len(self.rules)}, "
            f"threshold={self.threshold})"
        )