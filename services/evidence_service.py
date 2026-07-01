from core.evidence import EvidenceStore

from models.evidence import Evidence


class EvidenceService:

    def __init__(self):

        self.store = EvidenceStore()

    def add(

        self,

        evidence_type,

        value,

        speaker,

        text

    ):

        self.store.add(

            Evidence(

                type=evidence_type,

                value=value,

                speaker=speaker,

                text=text

            )

        )

    def latest(self, evidence_type):

        return self.store.latest(

            evidence_type

        )
