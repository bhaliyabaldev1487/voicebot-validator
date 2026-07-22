"""
Generic YAML Rule Loader

Loads YAML rule definitions and converts them into StatusRule objects.

Supports:
    • YAML schema validation
    • Regex compilation
    • Duplicate detection
    • Memory caching
    • Directory loading
    • Statistics reporting

Author: Baldev Bhaliya
"""

from __future__ import annotations

import copy
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from models.status_rule import StatusRule
from models.canonical_status import CanonicalStatus

LOGGER = logging.getLogger(__name__)


# ============================================================
# Constants
# ============================================================

SUPPORTED_EXTENSIONS = {".yml", ".yaml"}

DEFAULT_CONFIDENCE = 0.90

DEFAULT_PRIORITY = 50

SUPPORTED_SCHEMA_VERSION = "1.0"


# ============================================================
# Exceptions
# ============================================================

class RuleLoaderException(Exception):
    """Base exception for Rule Loader."""


class RuleFileNotFound(RuleLoaderException):
    """Raised when YAML file is missing."""


class InvalidRuleFile(RuleLoaderException):
    """Raised when YAML structure is invalid."""


class DuplicateRuleError(RuleLoaderException):
    """Raised for duplicate rule definitions."""


class InvalidRegexError(RuleLoaderException):
    """Raised when regex cannot be compiled."""


# ============================================================
# Statistics
# ============================================================

@dataclass
class RuleStatistics:

    files_loaded: int = 0

    statuses_loaded: int = 0

    phrases_loaded: int = 0

    regex_loaded: int = 0

    negatives_loaded: int = 0

    duplicate_phrases: int = 0

    duplicate_regex: int = 0

    warnings: int = 0

    errors: int = 0

    def reset(self):

        self.files_loaded = 0
        self.statuses_loaded = 0
        self.phrases_loaded = 0
        self.regex_loaded = 0
        self.negatives_loaded = 0
        self.duplicate_phrases = 0
        self.duplicate_regex = 0
        self.warnings = 0
        self.errors = 0

    def to_dict(self):

        return {

            "files_loaded": self.files_loaded,

            "statuses_loaded": self.statuses_loaded,

            "phrases_loaded": self.phrases_loaded,

            "regex_loaded": self.regex_loaded,

            "negatives_loaded": self.negatives_loaded,

            "duplicate_phrases": self.duplicate_phrases,

            "duplicate_regex": self.duplicate_regex,

            "warnings": self.warnings,

            "errors": self.errors,
        }


# ============================================================
# Cached Rule File
# ============================================================

@dataclass
class CachedRuleFile:

    path: Path

    last_modified: float

    category: str

    rules: List[StatusRule] = field(default_factory=list)

    raw_yaml: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# Validation Report
# ============================================================

@dataclass
class ValidationReport:

    errors: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str):

        self.errors.append(message)

    def add_warning(self, message: str):

        self.warnings.append(message)

    @property
    def is_valid(self):

        return len(self.errors) == 0


# ============================================================
# Rule Loader
# ============================================================

class RuleLoader:

    """
    Generic YAML Rule Loader.

    Example
    -------

    loader = RuleLoader()

    rules = loader.load(
        "rules/order_status.yml"
    )
    """

    def __init__(

        self,

        cache_enabled: bool = True,

        auto_reload: bool = False,

    ):

        self.cache_enabled = cache_enabled

        self.auto_reload = auto_reload

        self.statistics = RuleStatistics()

        self._cache: Dict[str, CachedRuleFile] = {}

        LOGGER.info(
            "RuleLoader initialized "
            "(cache=%s auto_reload=%s)",
            cache_enabled,
            auto_reload,
        )

    # =======================================================
    # Cache Management
    # =======================================================

    def clear_cache(self):

        """
        Remove every cached rule file.
        """

        self._cache.clear()

        LOGGER.info("Rule cache cleared.")

    # -------------------------------------------------------

    def has_cache(

        self,

        file_path: str,

    ) -> bool:

        return file_path in self._cache

    # -------------------------------------------------------

    def cache_size(self) -> int:

        return len(self._cache)

    # -------------------------------------------------------

    def statistics_report(self) -> Dict[str, Any]:

        return self.statistics.to_dict()

    # -------------------------------------------------------

    def reset_statistics(self):

        self.statistics.reset()

    # -------------------------------------------------------

    def __repr__(self):

        return (
            f"RuleLoader("
            f"cache_enabled={self.cache_enabled}, "
            f"cached_files={len(self._cache)})"
        )
    
        # =======================================================
    # Public API
    # =======================================================

    def load(self, file_path: str) -> List[StatusRule]:
        """
        Load a single YAML rule file.

        Parameters
        ----------
        file_path : str
            Path to YAML rule file.

        Returns
        -------
        List[StatusRule]
        """

        path = Path(file_path)

        if not path.exists():
            raise RuleFileNotFound(f"Rule file not found: {file_path}")

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise InvalidRuleFile(
                f"Unsupported extension: {path.suffix}"
            )

        if self.cache_enabled:

            cached = self._load_from_cache(path)

            if cached is not None:
                LOGGER.debug(
                    "Loaded '%s' from cache.",
                    path.name
                )
                return copy.deepcopy(cached.rules)

        yaml_data = self._read_yaml(path)

        report = ValidationReport()

        self._validate_document(
            yaml_data,
            report,
            path,
        )

        if not report.is_valid:

            raise InvalidRuleFile(
                "\n".join(report.errors)
            )

        rules = self._build_rules(
            yaml_data,
            report,
            path,
        )

        self.statistics.files_loaded += 1

        if self.cache_enabled:

            self._save_cache(
                path,
                yaml_data,
                rules,
            )

        return copy.deepcopy(rules)

    # -------------------------------------------------------

    def load_directory(
        self,
        directory: str,
    ) -> Dict[str, List[StatusRule]]:
        """
        Load every YAML rule file from a directory.
        """

        root = Path(directory)

        if not root.exists():
            raise RuleFileNotFound(directory)

        results: Dict[str, List[StatusRule]] = {}

        for yaml_file in self._discover_yaml_files(root):

            LOGGER.info(
                "Loading %s",
                yaml_file.name,
            )

            results[yaml_file.stem] = self.load(
                str(yaml_file)
            )

        return results

    # =======================================================
    # YAML Reader
    # =======================================================

    def _read_yaml(
        self,
        path: Path,
    ) -> Dict[str, Any]:
        """
        Read YAML document.
        """

        LOGGER.debug(
            "Reading YAML file %s",
            path,
        )

        try:

            with open(
                path,
                "r",
                encoding="utf-8",
            ) as stream:

                data = yaml.safe_load(stream)

        except yaml.YAMLError as exc:

            raise InvalidRuleFile(
                f"Invalid YAML: {path}"
            ) from exc

        except Exception as exc:

            raise RuleLoaderException(
                str(exc)
            ) from exc

        if not isinstance(data, dict):

            raise InvalidRuleFile(
                "Root YAML node must be a dictionary."
            )

        return data

    # =======================================================
    # Cache
    # =======================================================

    def _load_from_cache(
        self,
        path: Path,
    ) -> Optional[CachedRuleFile]:

        key = str(path.resolve())

        if key not in self._cache:
            return None

        cached = self._cache[key]

        if self.auto_reload:

            modified = path.stat().st_mtime

            if modified != cached.last_modified:

                LOGGER.info(
                    "Reloading modified rule file %s",
                    path.name,
                )

                del self._cache[key]

                return None

        return cached

    # -------------------------------------------------------

    def _save_cache(
        self,
        path: Path,
        yaml_data: Dict[str, Any],
        rules: List[StatusRule],
    ) -> None:

        key = str(path.resolve())

        category = yaml_data.get(
            "category",
            "UNKNOWN",
        )

        self._cache[key] = CachedRuleFile(
            path=path,
            last_modified=path.stat().st_mtime,
            category=category,
            rules=copy.deepcopy(rules),
            raw_yaml=copy.deepcopy(yaml_data),
        )

        LOGGER.debug(
            "Cached %s",
            path.name,
        )

    # =======================================================
    # Discovery
    # =======================================================

    def _discover_yaml_files(
        self,
        directory: Path,
    ) -> List[Path]:
        """
        Discover every YAML file recursively.
        """

        files: List[Path] = []

        for extension in SUPPORTED_EXTENSIONS:

            files.extend(
                directory.rglob(f"*{extension}")
            )

        files.sort()

        LOGGER.info(
            "Discovered %d YAML rule files.",
            len(files),
        )

        return files

    # =======================================================
    # Helpers
    # =======================================================

    def available_categories(self) -> List[str]:
        """
        Return cached categories.
        """

        return sorted(
            {
                cache.category
                for cache in self._cache.values()
            }
        )

    # -------------------------------------------------------

    def cached_files(self) -> List[str]:
        """
        Return cached filenames.
        """

        return sorted(
            [
                item.path.name
                for item in self._cache.values()
            ]
        )
    
        # =======================================================
    # Validation
    # =======================================================

    def _validate_document(
        self,
        document: Dict[str, Any],
        report: ValidationReport,
        path: Path,
    ) -> None:
        """
        Validate the overall YAML document.
        """

        required = (
            "version",
            "category",
            "statuses",
        )

        for key in required:

            if key not in document:

                report.add_error(
                    f"{path.name}: Missing required key '{key}'."
                )

        if not report.is_valid:
            return

        self._validate_schema_version(
            document,
            report,
        )

        statuses = document.get("statuses", {})

        if not isinstance(statuses, dict):

            report.add_error(
                "statuses must be a dictionary."
            )

            return

        seen_statuses = set()

        seen_phrases = set()

        seen_regex = set()

        seen_aliases = set()

        for status_name, status_data in statuses.items():

            self._validate_status(

                status_name,

                status_data,

                report,

                seen_statuses,

                seen_phrases,

                seen_regex,

                seen_aliases,

            )

    # -------------------------------------------------------

    def _validate_schema_version(

        self,

        document,

        report,

    ):

        version = str(
            document.get("version")
        )

        if version != SUPPORTED_SCHEMA_VERSION:

            report.add_warning(

                f"Schema version {version} differs from "
                f"supported version "
                f"{SUPPORTED_SCHEMA_VERSION}"

            )

    # -------------------------------------------------------

    def _validate_status(

        self,

        status_name,

        status,

        report,

        seen_statuses,

        seen_phrases,

        seen_regex,

        seen_aliases,

    ):

        if status_name in seen_statuses:

            report.add_error(

                f"Duplicate status: {status_name}"

            )

            return

        seen_statuses.add(status_name)

        if not isinstance(status, dict):

            report.add_error(

                f"{status_name} must be dictionary."

            )

            return

        self._validate_required_fields(

            status_name,

            status,

            report,

        )

        self._validate_confidence(

            status_name,

            status,

            report,

        )

        self._validate_priority(

            status_name,

            status,

            report,

        )

        self._detect_duplicate_phrases(

            status_name,

            status,

            report,

            seen_phrases,

        )

        self._detect_duplicate_regex(

            status_name,

            status,

            report,

            seen_regex,

        )

        self._detect_duplicate_aliases(

            status_name,

            status,

            report,

            seen_aliases,

        )

        self._validate_regex(

            status_name,

            status,

            report,

        )

    # =======================================================
    # Individual Validators
    # =======================================================

    def _validate_required_fields(

        self,

        status_name,

        status,

        report,

    ):

        required = [

            "confidence",

            "priority",

            "phrases",

            "regex",

            "negative",

        ]

        for field in required:

            if field not in status:

                report.add_error(

                    f"{status_name}: missing '{field}'."

                )

    # -------------------------------------------------------

    def _validate_confidence(

        self,

        status_name,

        status,

        report,

    ):

        confidence = status.get(

            "confidence",

            DEFAULT_CONFIDENCE,

        )

        if not isinstance(

            confidence,

            (float, int),

        ):

            report.add_error(

                f"{status_name}: confidence "

                "must be numeric."

            )

            return

        if confidence < 0:

            report.add_error(

                f"{status_name}: confidence < 0"

            )

        if confidence > 1:

            report.add_error(

                f"{status_name}: confidence > 1"

            )

    # -------------------------------------------------------

    def _validate_priority(

        self,

        status_name,

        status,

        report,

    ):

        priority = status.get(

            "priority",

            DEFAULT_PRIORITY,

        )

        if not isinstance(

            priority,

            int,

        ):

            report.add_error(

                f"{status_name}: priority "

                "must be integer."

            )

            return

        if priority < 0:

            report.add_error(

                f"{status_name}: invalid priority."

            )