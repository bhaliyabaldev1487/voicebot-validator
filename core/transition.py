from dataclasses import dataclass
from models.evidence import Evidence


@dataclass
class Transition:

    from_state: str

    to_state: str

    evidence: Evidence
