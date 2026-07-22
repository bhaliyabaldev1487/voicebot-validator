"""
rules/text_matcher.py

Generic text processing utilities used throughout the Voicebot Validator.

Responsibilities
----------------
* Text normalization
* ASR cleanup
* Sentence splitting
* Tokenization
* Regex utilities
* Phrase normalization

NOTE:
Matching algorithms (Levenshtein/Fuzzy) live in similarity_engine.py
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable, List, Optional


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------


@dataclass(slots=True)
class TextMatcherConfig:
    """
    Configuration used by TextMatcher.
    """

    lowercase: bool = True

    remove_accents: bool = True

    collapse_spaces: bool = True

    remove_punctuation: bool = False

    strip_quotes: bool = True

    preserve_decimal_numbers: bool = True

    min_token_length: int = 1


# ----------------------------------------------------------------------
# Text Matcher
# ----------------------------------------------------------------------


class TextMatcher:
    """
    Performs text cleanup before semantic matching.

    Example
    -------

    matcher = TextMatcher()

    text = matcher.normalize(
        "Your order is   currently being stitched!!"
    )

    """

    _SPACE_RE = re.compile(r"\s+")

    _SENTENCE_RE = re.compile(r"[.!?]+")

    _TOKEN_RE = re.compile(r"[A-Za-z0-9]+")

    def __init__(
        self,
        config: Optional[TextMatcherConfig] = None,
    ) -> None:

        self.config = config or TextMatcherConfig()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def normalize(
        self,
        text: Optional[str],
    ) -> str:
        """
        Full normalization pipeline.
        """

        if not text:
            return ""

        text = self._unicode_normalize(text)

        if self.config.remove_accents:
            text = self._remove_accents(text)

        if self.config.strip_quotes:
            text = self._strip_quotes(text)

        text = self._cleanup_asr(text)

        if self.config.lowercase:
            text = text.lower()

        if self.config.remove_punctuation:
            text = self.remove_punctuation(text)

        if self.config.collapse_spaces:
            text = self._collapse_spaces(text)

        return text.strip()

    # ------------------------------------------------------------------

    def tokenize(
        self,
        text: str,
    ) -> List[str]:

        normalized = self.normalize(text)

        tokens = self._TOKEN_RE.findall(normalized)

        return [
            token
            for token in tokens
            if len(token) >= self.config.min_token_length
        ]

    # ------------------------------------------------------------------

    def split_sentences(
        self,
        text: str,
    ) -> List[str]:

        normalized = self.normalize(text)

        sentences = self._SENTENCE_RE.split(normalized)

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    # ------------------------------------------------------------------

    def remove_punctuation(
        self,
        text: str,
    ) -> str:

        if self.config.preserve_decimal_numbers:

            text = re.sub(
                r"(?<!\d)[^\w\s]|[^\w\s](?!\d)",
                " ",
                text,
            )

        else:

            text = re.sub(
                r"[^\w\s]",
                " ",
                text,
            )

        return text

    # ------------------------------------------------------------------

    def normalize_phrase(
        self,
        phrase: str,
    ) -> str:

        return self.normalize(phrase)

    # ------------------------------------------------------------------

    def normalize_phrases(
        self,
        phrases: Iterable[str],
    ) -> List[str]:

        return [
            self.normalize(p)
            for p in phrases
            if p
        ]

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _unicode_normalize(
        text: str,
    ) -> str:

        return unicodedata.normalize(
            "NFKC",
            text,
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _remove_accents(
        text: str,
    ) -> str:

        normalized = unicodedata.normalize(
            "NFKD",
            text,
        )

        return "".join(
            c
            for c in normalized
            if not unicodedata.combining(c)
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _strip_quotes(
        text: str,
    ) -> str:

        return (
            text.replace('"', " ")
            .replace("'", " ")
            .replace("`", " ")
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _collapse_spaces(
        text: str,
    ) -> str:

        return re.sub(
            r"\s+",
            " ",
            text,
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _cleanup_asr(
        text: str,
    ) -> str:
        """
        Clean common speech-to-text artifacts.

        This method intentionally performs only generic cleanup.
        Project-specific fixes (e.g. spoken order numbers) belong
        in dedicated normalizers.
        """

        replacements = {

            " uh ": " ",

            " um ": " ",

            " hmm ": " ",

            " mm ": " ",

            " ah ": " ",

            "\n": " ",

            "\t": " ",

            "…": " ",

            "—": " ",

            "- -": " ",

            "  ": " ",

        }

        cleaned = f" {text} "

        for old, new in replacements.items():

            cleaned = cleaned.replace(old, new)

        return cleaned.strip()
    
        # ------------------------------------------------------------------
    # Phrase Matching
    # ------------------------------------------------------------------

    def contains_phrase(
        self,
        text: str,
        phrase: str,
    ) -> bool:
        """
        Returns True if phrase exists in text after normalization.
        """
        if not text or not phrase:
            return False

        return self.normalize(phrase) in self.normalize(text)

    # ------------------------------------------------------------------

    def contains_any(
        self,
        text: str,
        phrases: Iterable[str],
    ) -> bool:
        """
        Returns True if any phrase matches.
        """
        normalized = self.normalize(text)

        for phrase in phrases:
            if self.normalize(phrase) in normalized:
                return True

        return False

    # ------------------------------------------------------------------

    def contains_all(
        self,
        text: str,
        phrases: Iterable[str],
    ) -> bool:
        """
        Returns True only if all phrases are found.
        """
        normalized = self.normalize(text)

        for phrase in phrases:
            if self.normalize(phrase) not in normalized:
                return False

        return True

    # ------------------------------------------------------------------

    def find_matching_phrase(
        self,
        text: str,
        phrases: Iterable[str],
    ) -> Optional[str]:
        """
        Returns first matching phrase.
        """
        normalized = self.normalize(text)

        for phrase in phrases:
            candidate = self.normalize(phrase)

            if candidate in normalized:
                return phrase

        return None

    # ------------------------------------------------------------------

    def find_all_matching_phrases(
        self,
        text: str,
        phrases: Iterable[str],
    ) -> List[str]:
        """
        Returns all matching phrases.
        """
        normalized = self.normalize(text)

        matches: List[str] = []

        for phrase in phrases:
            candidate = self.normalize(phrase)

            if candidate in normalized:
                matches.append(phrase)

        return matches

    # ------------------------------------------------------------------
    # Regex
    # ------------------------------------------------------------------

    def regex_search(
        self,
        text: str,
        pattern: str,
        flags: int = re.IGNORECASE,
    ):
        """
        Wrapper around re.search().
        """
        return re.search(
            pattern,
            text,
            flags,
        )

    # ------------------------------------------------------------------

    def regex_findall(
        self,
        text: str,
        pattern: str,
        flags: int = re.IGNORECASE,
    ) -> List[str]:
        """
        Wrapper around re.findall().
        """
        return re.findall(
            pattern,
            text,
            flags,
        )

    # ------------------------------------------------------------------

    def contains_regex(
        self,
        text: str,
        patterns: Iterable[str],
    ) -> bool:
        """
        Returns True if any regex pattern matches.
        """
        for pattern in patterns:

            if self.regex_search(text, pattern):
                return True

        return False

    # ------------------------------------------------------------------
    # Negative Phrase Detection
    # ------------------------------------------------------------------

    def contains_negative_phrase(
        self,
        text: str,
        negative_phrases: Iterable[str],
    ) -> bool:
        """
        Detects phrases that invalidate a semantic match.

        Example:
            "not shipped"
            "never delivered"
            "hasn't been dispatched"
        """
        return self.contains_any(
            text,
            negative_phrases,
        )

    # ------------------------------------------------------------------
    # Context Extraction
    # ------------------------------------------------------------------

    def extract_context(
        self,
        text: str,
        phrase: str,
        window: int = 40,
    ) -> str:
        """
        Extract surrounding text around a matched phrase.
        """
        normalized = self.normalize(text)
        target = self.normalize(phrase)

        idx = normalized.find(target)

        if idx == -1:
            return ""

        start = max(0, idx - window)
        end = min(
            len(normalized),
            idx + len(target) + window,
        )

        return normalized[start:end].strip()

    # ------------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------------

    @staticmethod
    def confidence_from_match(
        matched_length: int,
        total_length: int,
    ) -> float:
        """
        Simple confidence estimator based on coverage.
        """
        if total_length <= 0:
            return 0.0

        score = matched_length / total_length

        return round(
            min(score, 1.0),
            3,
        )

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def unique(
        values: Iterable[str],
    ) -> List[str]:
        """
        Returns ordered unique values.
        """
        seen = set()
        output: List[str] = []

        for value in values:

            if value not in seen:
                output.append(value)
                seen.add(value)

        return output

    # ------------------------------------------------------------------

    def word_count(
        self,
        text: str,
    ) -> int:
        """
        Returns number of normalized tokens.
        """
        return len(
            self.tokenize(text)
        )

    # ------------------------------------------------------------------

    def sentence_count(
        self,
        text: str,
    ) -> int:
        """
        Returns number of normalized sentences.
        """
        return len(
            self.split_sentences(text)
        )

    # ------------------------------------------------------------------

    def is_empty(
        self,
        text: Optional[str],
    ) -> bool:
        """
        True if normalized text is empty.
        """
        return not bool(
            self.normalize(text)
        )

    # ------------------------------------------------------------------

    def normalize_document(
        self,
        text: str,
    ) -> str:
        """
        Convenience wrapper for document normalization.
        """
        return self.normalize(text)