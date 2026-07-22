"""
rules/similarity_engine.py

Reusable similarity engine for semantic matching.

This module intentionally contains NO business logic.

It can be reused for:

- Order Status
- Payment Status
- Shipment Status
- Product Matching
- Designer Matching
- Order Number Comparison

Author: Voicebot Validator
"""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Iterable, List, Optional


# ----------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------


@dataclass(slots=True)
class SimilarityResult:
    """
    Result of a similarity comparison.
    """

    source: str

    target: str

    score: float

    algorithm: str

    distance: Optional[int] = None

    metadata: dict = field(default_factory=dict)

    @property
    def matched(self) -> bool:
        return self.score >= 0.80

    def to_dict(self):

        return {

            "source": self.source,

            "target": self.target,

            "score": round(self.score, 4),

            "algorithm": self.algorithm,

            "distance": self.distance,

            "metadata": self.metadata,

        }


# ----------------------------------------------------------------------
# Engine
# ----------------------------------------------------------------------


class SimilarityEngine:

    """
    Generic string similarity engine.

    No project-specific logic belongs here.
    """

    # -------------------------------------------------------------

    @staticmethod
    def exact_match(
        left: str,
        right: str,
    ) -> SimilarityResult:

        score = 1.0 if left == right else 0.0

        return SimilarityResult(

            source=left,

            target=right,

            score=score,

            algorithm="exact",

        )

    # -------------------------------------------------------------

    @staticmethod
    def sequence_similarity(
        left: str,
        right: str,
    ) -> SimilarityResult:

        score = SequenceMatcher(
            None,
            left,
            right,
        ).ratio()

        return SimilarityResult(

            source=left,

            target=right,

            score=score,

            algorithm="sequence",

        )

    # -------------------------------------------------------------

    @staticmethod
    def levenshtein_distance(
        left: str,
        right: str,
    ) -> int:

        if left == right:
            return 0

        if len(left) == 0:
            return len(right)

        if len(right) == 0:
            return len(left)

        previous = list(range(len(right) + 1))

        for i, c1 in enumerate(left):

            current = [i + 1]

            for j, c2 in enumerate(right):

                insert_cost = previous[j + 1] + 1

                delete_cost = current[j] + 1

                replace_cost = previous[j] + (c1 != c2)

                current.append(
                    min(
                        insert_cost,
                        delete_cost,
                        replace_cost,
                    )
                )

            previous = current

        return previous[-1]

    # -------------------------------------------------------------

    @classmethod
    def levenshtein_similarity(
        cls,
        left: str,
        right: str,
    ) -> SimilarityResult:

        distance = cls.levenshtein_distance(
            left,
            right,
        )

        longest = max(
            len(left),
            len(right),
            1,
        )

        score = 1.0 - (distance / longest)

        return SimilarityResult(

            source=left,

            target=right,

            score=max(0.0, score),

            algorithm="levenshtein",

            distance=distance,

        )

    # -------------------------------------------------------------

    @staticmethod
    def tokenize(
        text: str,
    ) -> List[str]:

        return [
            token
            for token in text.split()
            if token.strip()
        ]

    # -------------------------------------------------------------

    @classmethod
    def token_overlap(
        cls,
        left: str,
        right: str,
    ) -> float:

        left_tokens = set(
            cls.tokenize(left)
        )

        right_tokens = set(
            cls.tokenize(right)
        )

        if not left_tokens or not right_tokens:
            return 0.0

        intersection = len(
            left_tokens.intersection(
                right_tokens
            )
        )

        return intersection / max(
            len(left_tokens),
            len(right_tokens),
        )

    # -------------------------------------------------------------

    @classmethod
    def average_similarity(
        cls,
        left: str,
        right: str,
    ) -> SimilarityResult:

        seq = cls.sequence_similarity(
            left,
            right,
        ).score

        lev = cls.levenshtein_similarity(
            left,
            right,
        ).score

        token = cls.token_overlap(
            left,
            right,
        )

        score = (
            seq +
            lev +
            token
        ) / 3

        return SimilarityResult(

            source=left,

            target=right,

            score=round(score, 4),

            algorithm="average",

        )

    # -------------------------------------------------------------

    @staticmethod
    def max_score(
        results: Iterable[SimilarityResult],
    ) -> Optional[SimilarityResult]:

        results = list(results)

        if not results:
            return None

        return max(
            results,
            key=lambda r: r.score,
        )

    # -------------------------------------------------------------

    @staticmethod
    def sort_results(
        results: Iterable[SimilarityResult],
    ) -> List[SimilarityResult]:

        return sorted(
            results,
            key=lambda r: r.score,
            reverse=True,
        )
    
        # -------------------------------------------------------------
    # Jaccard Similarity
    # -------------------------------------------------------------

    @classmethod
    def jaccard_similarity(
        cls,
        left: str,
        right: str,
    ) -> SimilarityResult:

        left_tokens = set(cls.tokenize(left))
        right_tokens = set(cls.tokenize(right))

        if not left_tokens and not right_tokens:
            score = 1.0
        elif not left_tokens or not right_tokens:
            score = 0.0
        else:
            union = left_tokens | right_tokens
            intersection = left_tokens & right_tokens
            score = len(intersection) / len(union)

        return SimilarityResult(
            source=left,
            target=right,
            score=round(score, 4),
            algorithm="jaccard",
        )

    # -------------------------------------------------------------
    # N-Gram
    # -------------------------------------------------------------

    @staticmethod
    def _ngrams(
        text: str,
        n: int = 2,
    ) -> set[str]:

        text = text.strip()

        if len(text) < n:
            return {text} if text else set()

        return {
            text[i:i+n]
            for i in range(len(text) - n + 1)
        }

    # -------------------------------------------------------------

    @classmethod
    def ngram_similarity(
        cls,
        left: str,
        right: str,
        n: int = 2,
    ) -> SimilarityResult:

        left_set = cls._ngrams(left, n)
        right_set = cls._ngrams(right, n)

        if not left_set and not right_set:
            score = 1.0
        elif not left_set or not right_set:
            score = 0.0
        else:
            score = (
                len(left_set & right_set)
                / len(left_set | right_set)
            )

        return SimilarityResult(
            source=left,
            target=right,
            score=round(score, 4),
            algorithm=f"{n}-gram",
        )

    # -------------------------------------------------------------
    # Weighted Similarity
    # -------------------------------------------------------------

    @classmethod
    def weighted_similarity(
        cls,
        left: str,
        right: str,
        sequence_weight: float = 0.35,
        levenshtein_weight: float = 0.30,
        token_weight: float = 0.20,
        jaccard_weight: float = 0.15,
    ) -> SimilarityResult:

        seq = cls.sequence_similarity(left, right).score
        lev = cls.levenshtein_similarity(left, right).score
        token = cls.token_overlap(left, right)
        jac = cls.jaccard_similarity(left, right).score

        score = (
            seq * sequence_weight
            + lev * levenshtein_weight
            + token * token_weight
            + jac * jaccard_weight
        )

        return SimilarityResult(
            source=left,
            target=right,
            score=round(score, 4),
            algorithm="weighted",
            metadata={
                "sequence": round(seq, 4),
                "levenshtein": round(lev, 4),
                "token": round(token, 4),
                "jaccard": round(jac, 4),
            },
        )

    # -------------------------------------------------------------
    # Candidate Matching
    # -------------------------------------------------------------

    @classmethod
    def compare_against_candidates(
        cls,
        source: str,
        candidates: Iterable[str],
    ) -> List[SimilarityResult]:

        results: List[SimilarityResult] = []

        for candidate in candidates:
            results.append(
                cls.weighted_similarity(
                    source,
                    candidate,
                )
            )

        return cls.sort_results(results)

    # -------------------------------------------------------------

    @classmethod
    def find_best_match(
        cls,
        source: str,
        candidates: Iterable[str],
    ) -> Optional[SimilarityResult]:

        results = cls.compare_against_candidates(
            source,
            candidates,
        )

        if not results:
            return None

        return results[0]

    # -------------------------------------------------------------

    @classmethod
    def rank_candidates(
        cls,
        source: str,
        candidates: Iterable[str],
        limit: int = 5,
    ) -> List[SimilarityResult]:

        return cls.compare_against_candidates(
            source,
            candidates,
        )[:limit]

    # -------------------------------------------------------------
    # Confidence
    # -------------------------------------------------------------

    @staticmethod
    def confidence_from_scores(
        scores: Iterable[float],
    ) -> float:

        scores = list(scores)

        if not scores:
            return 0.0

        return round(
            sum(scores) / len(scores),
            4,
        )

    # -------------------------------------------------------------

    @staticmethod
    def is_confident(
        score: float,
        threshold: float = 0.80,
    ) -> bool:

        return score >= threshold

    # -------------------------------------------------------------

    @classmethod
    def explain(
        cls,
        left: str,
        right: str,
    ) -> dict:

        seq = cls.sequence_similarity(left, right)
        lev = cls.levenshtein_similarity(left, right)
        jac = cls.jaccard_similarity(left, right)
        avg = cls.average_similarity(left, right)
        weighted = cls.weighted_similarity(left, right)

        return {
            "sequence": seq.to_dict(),
            "levenshtein": lev.to_dict(),
            "jaccard": jac.to_dict(),
            "average": avg.to_dict(),
            "weighted": weighted.to_dict(),
        }