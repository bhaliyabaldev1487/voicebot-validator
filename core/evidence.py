class EvidenceStore:

    def __init__(self):

        self.items = []

    def add(self, evidence):

        self.items.append(evidence)

    def get(self, evidence_type):

        return [

            x

            for x in self.items

            if x.type == evidence_type

        ]

    def latest(self, evidence_type):

        data = self.get(evidence_type)

        if data:

            return data[-1]

        return None
