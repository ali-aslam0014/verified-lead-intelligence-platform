from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


@dataclass
class DiscoveryRequest:
    """Encapsulates target definition parameters passed to source adapters."""
    niche: str
    geography: str
    sub_niche: Optional[str] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    source_configuration: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RawDiscoveryResult:
    """
    Provenance data model for discovered records.
    Every discovered record MUST retain provenance details.
    
    NOTE: confidence_hint is a source-provided quality hint ONLY.
    It must NOT be treated as verified Business Confidence until passed
    through the Entity Resolution & Verification Engine.
    """
    source_name: str
    source_identifier: str
    raw_data: Dict[str, Any]
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_hint: float = 0.5
    licensing_notice: str = "Public/Licensed Data API"


class BaseSourceAdapter(ABC):
    """Abstract Base Class for all external discovery data source adapters."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Unique identifier of the data source adapter."""
        pass

    @property
    @abstractmethod
    def rate_limit_per_minute(self) -> int:
        """Maximum allowed requests per minute."""
        pass

    @property
    @abstractmethod
    def timeout_seconds(self) -> float:
        """HTTP / Socket request timeout in seconds."""
        pass

    @abstractmethod
    async def search(self, request: DiscoveryRequest) -> List[RawDiscoveryResult]:
        """
        Executes business discovery search based on DiscoveryRequest parameters.
        Must return list of RawDiscoveryResult provenance objects.
        """
        pass

    @abstractmethod
    async def fetch_details(self, source_identifier: str) -> RawDiscoveryResult:
        """Fetches detailed raw record payload by source identifier."""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Checks API reachability and credential health."""
        pass
