"""Telemetry utilities for logs and in-memory metrics."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime


REQUEST_LATENCY_BUCKETS_MS = (10, 25, 50, 100, 150, 250, 500, 1000)


def utc_timestamp() -> str:
    """Create an ISO 8601 UTC timestamp string.

    Returns
    -------
    str
        Timestamp with timezone information.
    """

    return datetime.now(tz=UTC).isoformat()


def emit_json_log(logger: logging.Logger, payload: dict[str, object]) -> None:
    """Emit a structured JSON log line.

    Parameters
    ----------
    logger : logging.Logger
        Logger instance used for output.
    payload : dict[str, object]
        Structured log payload.
    """

    logger.info(json.dumps(payload, ensure_ascii=True, sort_keys=True))


@dataclass
class MetricsStore:
    """In-memory telemetry store for request and domain metrics."""

    request_count_by_endpoint: dict[str, int] = field(default_factory=dict)
    request_latency_histogram: dict[str, int] = field(default_factory=dict)
    error_count_by_code: dict[str, int] = field(default_factory=dict)
    current_cycle_id: int = 1

    def observe_request(self, endpoint: str, latency_ms: float) -> None:
        """Record request count and latency histogram observation.

        Parameters
        ----------
        endpoint : str
            Endpoint path.
        latency_ms : float
            Request latency in milliseconds.
        """

        self.request_count_by_endpoint[endpoint] = (
            self.request_count_by_endpoint.get(endpoint, 0) + 1
        )
        bucket_label = _bucket_for_latency(latency_ms)
        self.request_latency_histogram[bucket_label] = (
            self.request_latency_histogram.get(bucket_label, 0) + 1
        )

    def observe_error_code(self, error_code: str) -> None:
        """Record an error-code occurrence.

        Parameters
        ----------
        error_code : str
            Machine-readable error code.
        """

        self.error_count_by_code[error_code] = self.error_count_by_code.get(error_code, 0) + 1

    def set_cycle_id(self, cycle_id: int) -> None:
        """Update current cycle gauge value.

        Parameters
        ----------
        cycle_id : int
            Current cycle identifier.
        """

        self.current_cycle_id = cycle_id

    def to_payload(self) -> dict[str, object]:
        """Serialize metrics for API response.

        Returns
        -------
        dict[str, object]
            JSON-serializable metrics payload.
        """

        return {
            "request_count_by_endpoint": self.request_count_by_endpoint,
            "request_latency_histogram_ms": self.request_latency_histogram,
            "error_count_by_code": self.error_count_by_code,
            "current_cycle_id": self.current_cycle_id,
        }


def _bucket_for_latency(latency_ms: float) -> str:
    """Map latency value to histogram bucket label.

    Parameters
    ----------
    latency_ms : float
        Request latency in milliseconds.

    Returns
    -------
    str
        Bucket label in the form ``le_<ms>`` or ``gt_<ms>``.
    """

    for threshold in REQUEST_LATENCY_BUCKETS_MS:
        if latency_ms <= threshold:
            return f"le_{threshold}"
    return f"gt_{REQUEST_LATENCY_BUCKETS_MS[-1]}"
