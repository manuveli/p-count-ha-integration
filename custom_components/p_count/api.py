"""API client for P-Count parking system."""

from __future__ import annotations

import base64
import logging
from dataclasses import dataclass
from datetime import datetime

import aiohttp

from .const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)


class PCountAuthError(Exception):
    """Raised when authentication fails."""


class PCountConnectionError(Exception):
    """Raised when connection to P-Count fails."""


@dataclass
class ParkingSection:
    """Represents a parking section."""

    short_name: str
    long_name: str
    occupied_spots: int
    free_spots: int

    @property
    def total_spots(self) -> int:
        """Return total spots in this section."""
        return self.occupied_spots + self.free_spots

    @property
    def occupancy_percent(self) -> float:
        """Return occupancy percentage."""
        if self.total_spots == 0:
            return 0.0
        return round((self.occupied_spots / self.total_spots) * 100, 1)


@dataclass
class ParkingData:
    """Represents the full parking occupation data."""

    measured_at: datetime
    sections: list[ParkingSection]
    polling_seconds: int

    @property
    def total_occupied(self) -> int:
        """Return total occupied spots across all sections."""
        return sum(s.occupied_spots for s in self.sections)

    @property
    def total_free(self) -> int:
        """Return total free spots across all sections."""
        return sum(s.free_spots for s in self.sections)

    @property
    def total_spots(self) -> int:
        """Return total spots across all sections."""
        return sum(s.total_spots for s in self.sections)


@dataclass
class CarParkInfo:
    """Represents car park metadata."""

    sid: str
    title: str


class PCountApiClient:
    """Client for the P-Count parking API."""

    def __init__(
        self,
        system_id: str,
        access_code: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the API client."""
        self._system_id = system_id
        self._access_code = access_code
        self._session = session
        self._auth_header = self._build_auth_header()

    def _build_auth_header(self) -> str:
        """Build the Basic Auth header value."""
        credentials = f"{self._system_id}:{self._access_code}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    async def async_get_carpark_info(self) -> CarParkInfo:
        """Fetch car park metadata. Also used to validate credentials."""
        url = f"{API_BASE_URL}/carparks/{self._system_id}.json"
        headers = {"Authorization": self._auth_header}

        try:
            async with self._session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 401:
                    raise PCountAuthError("Invalid credentials")
                if resp.status == 404:
                    raise PCountAuthError("Parking system not found")
                if resp.status != 200:
                    raise PCountConnectionError(f"Unexpected status: {resp.status}")

                data = await resp.json()
                return CarParkInfo(
                    sid=data["sid"],
                    title=data["title"],
                )
        except aiohttp.ClientError as err:
            raise PCountConnectionError(f"Connection error: {err}") from err

    async def async_get_occupation(self) -> ParkingData:
        """Fetch current parking occupation data."""
        url = f"{API_BASE_URL}/carparks/{self._system_id}/occupation.json"
        headers = {"Authorization": self._auth_header}

        try:
            async with self._session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 401:
                    raise PCountAuthError("Invalid credentials")
                if resp.status != 200:
                    raise PCountConnectionError(f"Unexpected status: {resp.status}")

                data = await resp.json()
                return self._parse_occupation(data)
        except aiohttp.ClientError as err:
            raise PCountConnectionError(f"Connection error: {err}") from err

    @staticmethod
    def _parse_occupation(data: dict) -> ParkingData:
        """Parse the occupation JSON response."""
        sections = [
            ParkingSection(
                short_name=section["short_name"],
                long_name=section["long_name"],
                occupied_spots=section["occupied_spots"],
                free_spots=section["free_spots"],
            )
            for section in data.get("sections", [])
        ]

        measured_at_str = data.get("measured_at", "")
        try:
            measured_at = datetime.fromisoformat(measured_at_str)
        except (ValueError, TypeError):
            measured_at = datetime.now()

        return ParkingData(
            measured_at=measured_at,
            sections=sections,
            polling_seconds=data.get("polling_seconds", 30),
        )
