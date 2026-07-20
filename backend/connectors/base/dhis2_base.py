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
)


class BaseDHIS2Connector(ReadOnlyConnector):
    """Base DHIS2 API client with auth, pagination, retry, and rate limiting."""

    name = "dhis2_base"
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    PAGE_SIZE = 500
    MAX_PAGES = 20  # safety limit to prevent infinite pagination

    # Translates ETL loader resource names to DHIS2 API resource names
    DHIS2_RESOURCE_MAP = {
        "districts": "organisationUnits",
        "facilities": "organisationUnits",
        "indicators": "indicators",
        "vaccinations": "programs",
        "disease_reports": "analytics",
        "surveillance_events": "events",
    }

    # Fields to request for each DHIS2 resource (needed by canonical mappers)
    DEFAULT_FIELDS = {
        "organisationUnits": "id,name,shortName,level,parent[id,name],coordinates,organisationUnitGroups[id,name]",
        "indicators": "id,name,displayName,numerator,denominator,indicatorType[id,name]",
        "programs": "id,name,displayName,programType,programStages[id,name]",
        "events": "*",
    }

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        raw_url = self.config.get("base_url", "").rstrip("/")
        # Strip trailing /api to avoid double-prefixing with hardcoded /api/ below
        if raw_url.endswith("/api"):
            raw_url = raw_url[:-4]
        self.base_url = raw_url
        self.username = self.config.get("username", "")
        self.password = self.config.get("password", "")
        self.timeout = self.config.get("timeout", self.DEFAULT_TIMEOUT)
        self._client: Optional[httpx.Client] = None

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            auth = None
            if self.username and self.password:
                from httpx import BasicAuth
                auth = BasicAuth(self.username, self.password)
            self._client = httpx.Client(
                base_url=self.base_url,
                auth=auth,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "HealthIntelAI/1.0",
                },
                timeout=self.timeout,
                follow_redirects=True,
            )
        return self._client

    def connect(self) -> bool:
        try:
            client = self._get_client()
            resp = client.get("/api/me", timeout=self.timeout)
            if resp.status_code == 401:
                raise AuthenticationError("DHIS2 server returned 401 Unauthorized")
            if resp.status_code == 403:
                raise AuthenticationError("DHIS2 server returned 403 Forbidden")
            resp.raise_for_status()
            self._connected = True
            logger.info(f"Connected to DHIS2 server at {self.base_url}")
            return True
        except httpx.ConnectError:
            logger.warning(f"Could not connect to DHIS2 server at {self.base_url}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"DHIS2 connection failed: {e}")
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
            resp = client.get("/api/me", timeout=5)
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
        system_info = client.get("/api/system/info").json()
        resources = self._discover_resources(client)

        statement = CapabilityStatement(
            connector_type="dhis2",
            api_version=system_info.get("version", "unknown"),
            supported_resources=resources,
            supported_operations=["read", "query", "analytics"],
            metadata={
                "revision": system_info.get("revision", ""),
                "context_path": self.base_url,
            },
        )
        self._capabilities = statement
        return statement

    def _discover_resources(self, client) -> list:
        resources = []
        try:
            resp = client.get("/api/resources")
            if resp.is_success:
                data = resp.json()
                for res in data.get("resources", []):
                    resources.append(res.get("name", ""))
        except Exception:
            resources = [
                "organisationUnits", "dataElements", "indicators",
                "programs", "programStages", "dataSets",
                "categories", "categoryCombos", "trackedEntityInstances",
                "events", "analytics", "system",
            ]
        return resources

    def fetch(self, resource: str, params: Optional[dict] = None) -> list[dict]:
        self.assert_read_only("GET")
        params = dict(params or {})
        # Translate ETL loader name to DHIS2 API resource name
        dhis2_resource = self.DHIS2_RESOURCE_MAP.get(resource, resource)

        # For unmapped resources (outbreaks, health_workers, medicine_stock),
        # return empty list — DHIS2 has no equivalent
        if resource not in self.DHIS2_RESOURCE_MAP:
            logger.warning(f"No DHIS2 mapping for '{resource}', returning empty")
            return []

        # Analytics endpoint requires dimension params, not pagination
        if dhis2_resource == "analytics":
            return self._fetch_analytics(params)

        # For paginated resources (organisationUnits, indicators, programs, events)
        params.setdefault("pageSize", self.PAGE_SIZE)
        params.setdefault("paging", "true")
        if dhis2_resource in self.DEFAULT_FIELDS:
            params.setdefault("fields", self.DEFAULT_FIELDS[dhis2_resource])

        results = []
        url = f"/api/{dhis2_resource}"
        page = 1

        for attempt in range(self.MAX_RETRIES):
            try:
                client = self._get_client()
                while True:
                    params["page"] = page
                    resp = client.get(url, params=params)
                    if resp.status_code == 429:
                        raise RateLimitError("Rate limit hit")
                    resp.raise_for_status()
                    data = resp.json()

                    pager = data.get("pager", {})
                    items_key = dhis2_resource if dhis2_resource in data else self._find_items_key(data)
                    items = data.get(items_key, [])
                    results.extend(items)

                    total_pages = min(pager.get("pageCount", 1), self.MAX_PAGES)
                    if page >= total_pages:
                        break
                    page += 1
                return results
            except RateLimitError:
                wait = self.RETRY_DELAY * (2 ** attempt)
                logger.warning(f"Rate limited, retrying in {wait}s (attempt {attempt + 1})")
                time.sleep(wait)
            except httpx.TimeoutException:
                wait = self.RETRY_DELAY * (2 ** attempt)
                logger.warning(f"Timeout, retrying in {wait}s (attempt {attempt + 1})")
                time.sleep(wait)

        return results

    def _fetch_analytics(self, params: dict) -> list[dict]:
        """Fetch analytics data with dimension-based query."""
        try:
            client = self._get_client()
            # Build a default analytics query using available data elements
            if "dimension" not in params:
                # Fetch first data element to use as dimension
                de_resp = client.get("/api/dataElements?fields=id&pageSize=1&paging=true&page=1")
                if de_resp.is_success:
                    de_data = de_resp.json()
                    de_list = de_data.get("dataElements", [])
                    if de_list:
                        dx = de_list[0]["id"]
                        params["dimension"] = [f"dx:{dx}", "pe:LAST_12_MONTHS"]
            resp = client.get("/api/analytics", params=params)
            if resp.is_success:
                data = resp.json()
                return [data]
            logger.warning(f"Analytics query failed ({resp.status_code}): {resp.text[:200]}")
            return []
        except Exception as e:
            logger.warning(f"Analytics fetch error: {e}")
            return []

    def _find_items_key(self, data: dict) -> str:
        for key in data:
            if isinstance(data[key], list) and key != "pager":
                return key
        return "items"

    def get_organisation_units(self, params: Optional[dict] = None) -> list[dict]:
        return self.fetch("organisationUnits", params)

    def get_indicators(self, params: Optional[dict] = None) -> list[dict]:
        return self.fetch("indicators", params)

    def get_data_elements(self, params: Optional[dict] = None) -> list[dict]:
        return self.fetch("dataElements", params)

    def get_programs(self, params: Optional[dict] = None) -> list[dict]:
        return self.fetch("programs", params)

    def get_data_sets(self, params: Optional[dict] = None) -> list[dict]:
        return self.fetch("dataSets", params)

    def get_analytics(self, params: Optional[dict] = None) -> dict:
        self.assert_read_only("GET")
        client = self._get_client()
        resp = client.get("/api/analytics", params=params)
        resp.raise_for_status()
        return resp.json()
