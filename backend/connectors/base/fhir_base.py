from typing import Optional, Any
from urllib.parse import urljoin
import time

import httpx
from core.logging import logger
from connectors.base.base_connector import ReadOnlyConnector, CapabilityStatement
from connectors.base.errors import (
    ConnectionFailedError,
    AuthenticationError,
    RateLimitError,
    TimeoutError,
    ResourceNotFoundError,
)


class BaseFHIRConnector(ReadOnlyConnector):
    """Base FHIR R4/R5 client with auth, pagination, retry, and rate limiting."""

    name = "fhir_base"
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    MAX_PAGES = 50  # safety limit to prevent infinite pagination

    # Translates ETL loader resource names to FHIR resource type names
    FHIR_RESOURCE_MAP = {
        "hospitals": "Organization",
        "patients": "Patient",
        "admissions": "Encounter",
        "staff": "Practitioner",
        "medicine_inventory": "MedicationRequest",
        "departments": "Organization",
        "wards": "Location",
        "beds": "Location",
        "equipment": "Device",
    }

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.base_url = self.config.get("base_url", "").rstrip("/")
        self.auth_type = self.config.get("auth_type", "none")
        self.token = self.config.get("token", "")
        self.username = self.config.get("username", "")
        self.password = self.config.get("password", "")
        self.timeout = self.config.get("timeout", self.DEFAULT_TIMEOUT)
        self._client: Optional[httpx.Client] = None

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            headers = {
                "Accept": "application/fhir+json",
                "User-Agent": "HealthIntelAI/1.0",
            }
            if self.auth_type == "bearer" and self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            self._client = httpx.Client(
                base_url=self.base_url,
                headers=headers,
                timeout=self.timeout,
                follow_redirects=True,
            )
        return self._client

    def connect(self) -> bool:
        try:
            client = self._get_client()
            resp = client.get("/metadata", timeout=self.timeout)
            if resp.status_code == 401:
                raise AuthenticationError("FHIR server returned 401 Unauthorized")
            if resp.status_code == 403:
                raise AuthenticationError("FHIR server returned 403 Forbidden")
            resp.raise_for_status()
            self._connected = True
            logger.info(f"Connected to FHIR server at {self.base_url}")
            return True
        except httpx.ConnectError as e:
            logger.warning(f"Could not connect to FHIR server at {self.base_url}: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"FHIR connection failed: {e}")
            self._connected = False
            return False

    def disconnect(self):
        if self._client:
            self._client.close()
            self._client = None
        self._connected = False

    def health_check(self) -> dict:
        try:
            if not self._connected:
                return {"status": "disconnected", "connector": self.name}
            client = self._get_client()
            resp = client.get("/metadata", timeout=5)
            return {
                "status": "healthy" if resp.is_success else "unhealthy",
                "connector": self.name,
                "base_url": self.base_url,
                "status_code": resp.status_code,
                "mode": "live_readonly",
            }
        except Exception as e:
            return {"status": "error", "connector": self.name, "error": str(e)}

    def discover_capabilities(self) -> CapabilityStatement:
        client = self._get_client()
        resp = client.get("/metadata")
        resp.raise_for_status()
        cap = resp.json()

        resources = []
        if "rest" in cap:
            for rest in cap.get("rest", []):
                for resource in rest.get("resource", []):
                    resources.append(resource.get("type", ""))

        statement = CapabilityStatement(
            connector_type="fhir",
            api_version=cap.get("fhirVersion", "unknown"),
            supported_resources=resources,
            supported_operations=["read", "search"],
            metadata={
                "publisher": cap.get("publisher", ""),
                "software": cap.get("software", {}).get("name", ""),
                "version": cap.get("software", {}).get("version", ""),
            },
        )
        self._capabilities = statement
        return statement

    def fetch(self, resource: str, params: Optional[dict] = None) -> list[dict]:
        self.assert_read_only("GET")
        params = params or {}
        results = []
        # Translate ETL loader name to FHIR resource type
        fhir_resource = self.FHIR_RESOURCE_MAP.get(resource, resource)
        url = f"/{fhir_resource}"

        for attempt in range(self.MAX_RETRIES):
            try:
                client = self._get_client()
                resp = client.get(url, params=params)
                if resp.status_code == 429:
                    raise RateLimitError("Rate limit hit")
                resp.raise_for_status()
                data = resp.json()

                if "entry" in data:
                    for entry in data["entry"]:
                        results.append(entry.get("resource", {}))
                else:
                    results.append(data)

                next_url = self._get_next_url(data)
                page_count = 1
                while next_url and page_count < self.MAX_PAGES:
                    resp = client.get(next_url)
                    resp.raise_for_status()
                    data = resp.json()
                    if "entry" in data:
                        for entry in data["entry"]:
                            results.append(entry.get("resource", {}))
                    next_url = self._get_next_url(data)
                    page_count += 1
                if next_url:
                    logger.warning(f"Stopped pagination after {self.MAX_PAGES} pages for '{fhir_resource}'")
                return results
            except RateLimitError:
                wait = self.RETRY_DELAY * (2 ** attempt)
                logger.warning(f"Rate limited, retrying in {wait}s (attempt {attempt + 1})")
                time.sleep(wait)
            except httpx.TimeoutException:
                wait = self.RETRY_DELAY * (2 ** attempt)
                logger.warning(f"Timeout, retrying in {wait}s (attempt {attempt + 1})")
                time.sleep(wait)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise ResourceNotFoundError(f"Resource {resource} not found")
                raise

        return results

    def _get_next_url(self, data: dict) -> Optional[str]:
        for link in data.get("link", []):
            if link.get("relation") == "next":
                return link.get("url")
        return None

    def fetch_patient(self, patient_id: str) -> dict:
        return self.fetch(f"Patient/{patient_id}")

    def search_patients(self, params: Optional[dict] = None) -> list[dict]:
        return self.fetch("Patient", params)

    def search_observations(self, params: Optional[dict] = None) -> list[dict]:
        return self.fetch("Observation", params)

    def search_encounters(self, params: Optional[dict] = None) -> list[dict]:
        return self.fetch("Encounter", params)

    def search_conditions(self, params: Optional[dict] = None) -> list[dict]:
        return self.fetch("Condition", params)

    def search_medications(self, params: Optional[dict] = None) -> list[dict]:
        return self.fetch("MedicationRequest", params)

    def search_locations(self, params: Optional[dict] = None) -> list[dict]:
        return self.fetch("Location", params)

    def search_practitioners(self, params: Optional[dict] = None) -> list[dict]:
        return self.fetch("Practitioner", params)
