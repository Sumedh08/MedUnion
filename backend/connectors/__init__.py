from connectors.registry import connector_registry


def init_connectors():
    """Initialize all configured connectors."""
    from core.config import settings

    if settings.CONNECTOR_FHIR_URL:
        from connectors.hospital.fhir_connector import FHIRConnector
        fhir = FHIRConnector({"base_url": settings.CONNECTOR_FHIR_URL, "auth_type": settings.CONNECTOR_FHIR_AUTH_TYPE, "token": settings.CONNECTOR_FHIR_TOKEN, "timeout": 5})
        if fhir.connect():
            connector_registry.register("fhir", fhir)

    if settings.CONNECTOR_DHIS2_URL:
        from connectors.community.dhis2_connector import DHIS2Connector
        dhis2 = DHIS2Connector({"base_url": settings.CONNECTOR_DHIS2_URL, "username": settings.CONNECTOR_DHIS2_USERNAME, "password": settings.CONNECTOR_DHIS2_PASSWORD, "timeout": 5})
        if dhis2.connect():
            connector_registry.register("dhis2", dhis2)

    return connector_registry
