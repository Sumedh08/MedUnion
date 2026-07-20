from typing import Optional
from connectors.base.fhir_base import BaseFHIRConnector


class FHIRConnector(BaseFHIRConnector):
    """FHIR R4/R5 connector for hospital intelligence workspace.

    Reads patient data, encounters, observations, medications, and more
    from any FHIR-compliant server.
    """

    name = "fhir"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
