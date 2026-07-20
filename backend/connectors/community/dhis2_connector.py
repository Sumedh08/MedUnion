from typing import Optional
from connectors.base.dhis2_base import BaseDHIS2Connector


class DHIS2Connector(BaseDHIS2Connector):
    """DHIS2 connector for community health intelligence workspace.

    Reads organisation units, indicators, programs, data sets, and analytics
    from any DHIS2 instance.
    """

    name = "dhis2"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
