"""
Data models for the DTC API SDK.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Union
from enum import Enum


class ResponseStatus(str, Enum):
    """Response status values."""
    OK = "OK"
    ERROR = "Error"


class TaskStatus(str, Enum):
    """Task status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class APIResponse:
    """Base API response model."""
    status: ResponseStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    
    @property
    def is_success(self) -> bool:
        """Check if the response indicates success."""
        return self.status == ResponseStatus.OK
    
    @property
    def error_message(self) -> Optional[str]:
        """Get error message if available."""
        if self.error:
            return self.error.get("message")
        return None


@dataclass
class PipelineConfig:
    """Pipeline configuration model."""
    source: str
    transformations: List[str] = field(default_factory=list)
    destination: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        result = {"source": self.source}
        if self.transformations:
            result["transformations"] = self.transformations
        if self.destination:
            result["destination"] = self.destination
        if self.settings:
            result["settings"] = self.settings
        return result


@dataclass
class PipelineInfo:
    """Pipeline information model."""
    name: str
    token: str
    status: str
    created_at: Optional[str] = None
    config: Optional[PipelineConfig] = None


@dataclass
class TaskInfo:
    """Task information model."""
    token: str
    status: TaskStatus
    name: Optional[str] = None
    progress: Optional[float] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


@dataclass
class ServiceInfo:
    """Service information model."""
    name: str
    status: str
    version: Optional[str] = None
    description: Optional[str] = None
    endpoints: Optional[List[str]] = None


@dataclass
class ValidationError:
    """API validation error model."""
    loc: List[Union[str, int]]
    msg: str
    type: str 