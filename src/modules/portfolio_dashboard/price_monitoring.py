"""
Price Fetcher Monitoring and Metrics - Task 16.5

Provides monitoring, metrics tracking, and performance analysis for the price fetching system.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class PriceMonitor:
    """
    Monitor and track price fetcher performance and statistics.

    Tracks:
    - API call counts and success rates
    - Cache hit/miss rates
    - Error counts and types
    - Response times
    - Data source usage
    """

    def __init__(self):
        """Initialize monitoring system."""
        self.reset_metrics()

    def reset_metrics(self):
        """Reset all metrics to initial state."""
        self._api_calls = defaultdict(int)  # source -> count
        self._api_successes = defaultdict(int)
        self._api_failures = defaultdict(int)
        self._cache_hits = 0
        self._cache_misses = 0
        self._errors = defaultdict(int)  # error_type -> count
        self._fallback_usage = defaultdict(int)  # fallback_level -> count
        self._stale_price_usage = 0
        self._manual_price_usage = 0
        self._response_times = []  # List of (source, duration) tuples
        self._session_start = datetime.now()

    def record_api_call(self, source: str, success: bool, duration_ms: float = None):
        """
        Record an API call attempt.

        Args:
            source: Data source name (e.g., 'yfinance', 'tase_yahoo')
            success: Whether the call succeeded
            duration_ms: Response time in milliseconds
        """
        self._api_calls[source] += 1

        if success:
            self._api_successes[source] += 1
        else:
            self._api_failures[source] += 1

        if duration_ms is not None:
            self._response_times.append((source, duration_ms))

        logger.debug(f"API call: {source}, success={success}, duration={duration_ms}ms")

    def record_cache_hit(self):
        """Record a cache hit."""
        self._cache_hits += 1
        logger.debug("Cache hit")

    def record_cache_miss(self):
        """Record a cache miss."""
        self._cache_misses += 1
        logger.debug("Cache miss")

    def record_error(self, error_type: str):
        """
        Record an error occurrence.

        Args:
            error_type: Type/category of error
        """
        self._errors[error_type] += 1
        logger.debug(f"Error recorded: {error_type}")

    def record_fallback(self, fallback_level: str):
        """
        Record usage of a fallback mechanism.

        Args:
            fallback_level: Which fallback was used (manual, cached, unavailable)
        """
        self._fallback_usage[fallback_level] += 1
        logger.debug(f"Fallback used: {fallback_level}")

    def record_stale_price(self):
        """Record usage of a stale price."""
        self._stale_price_usage += 1
        logger.debug("Stale price used")

    def record_manual_price(self):
        """Record usage of a manual price."""
        self._manual_price_usage += 1
        logger.debug("Manual price used")

    def get_metrics(self) -> Dict:
        """
        Get current monitoring metrics.

        Returns:
            Dictionary containing all current metrics
        """
        total_api_calls = sum(self._api_calls.values())
        total_successes = sum(self._api_successes.values())
        total_failures = sum(self._api_failures.values())

        cache_total = self._cache_hits + self._cache_misses
        cache_hit_rate = (self._cache_hits / cache_total * 100) if cache_total > 0 else 0

        success_rate = (total_successes / total_api_calls * 100) if total_api_calls > 0 else 0

        session_duration = (datetime.now() - self._session_start).total_seconds()

        # Calculate average response times by source
        avg_response_times = {}
        if self._response_times:
            by_source = defaultdict(list)
            for source, duration in self._response_times:
                by_source[source].append(duration)

            for source, durations in by_source.items():
                avg_response_times[source] = sum(durations) / len(durations)

        return {
            "session": {
                "start_time": self._session_start.isoformat(),
                "duration_seconds": session_duration,
                "duration_minutes": session_duration / 60
            },
            "api_calls": {
                "total": total_api_calls,
                "successes": total_successes,
                "failures": total_failures,
                "success_rate_percent": success_rate,
                "by_source": dict(self._api_calls),
                "successes_by_source": dict(self._api_successes),
                "failures_by_source": dict(self._api_failures)
            },
            "cache": {
                "hits": self._cache_hits,
                "misses": self._cache_misses,
                "total_requests": cache_total,
                "hit_rate_percent": cache_hit_rate
            },
            "errors": {
                "total": sum(self._errors.values()),
                "by_type": dict(self._errors)
            },
            "fallbacks": {
                "total": sum(self._fallback_usage.values()),
                "by_level": dict(self._fallback_usage),
                "stale_prices_used": self._stale_price_usage,
                "manual_prices_used": self._manual_price_usage
            },
            "performance": {
                "avg_response_times_ms": avg_response_times,
                "total_measurements": len(self._response_times)
            }
        }

    def get_summary(self) -> str:
        """
        Get human-readable summary of metrics.

        Returns:
            Formatted summary string
        """
        metrics = self.get_metrics()

        summary = []
        summary.append("=" * 70)
        summary.append("PRICE FETCHER MONITORING SUMMARY")
        summary.append("=" * 70)

        # Session info
        summary.append(f"\nSession Duration: {metrics['session']['duration_minutes']:.1f} minutes")

        # API calls
        api = metrics['api_calls']
        summary.append(f"\nAPI Calls:")
        summary.append(f"  Total: {api['total']}")
        summary.append(f"  Successes: {api['successes']}")
        summary.append(f"  Failures: {api['failures']}")
        summary.append(f"  Success Rate: {api['success_rate_percent']:.1f}%")

        # Cache performance
        cache = metrics['cache']
        summary.append(f"\nCache Performance:")
        summary.append(f"  Hits: {cache['hits']}")
        summary.append(f"  Misses: {cache['misses']}")
        summary.append(f"  Hit Rate: {cache['hit_rate_percent']:.1f}%")

        # Fallbacks
        fallbacks = metrics['fallbacks']
        summary.append(f"\nFallback Usage:")
        summary.append(f"  Total: {fallbacks['total']}")
        summary.append(f"  Stale Prices: {fallbacks['stale_prices_used']}")
        summary.append(f"  Manual Prices: {fallbacks['manual_prices_used']}")

        # Errors
        errors = metrics['errors']
        summary.append(f"\nErrors:")
        summary.append(f"  Total: {errors['total']}")
        if errors['by_type']:
            for error_type, count in errors['by_type'].items():
                summary.append(f"    {error_type}: {count}")

        # Performance
        perf = metrics['performance']
        if perf['avg_response_times_ms']:
            summary.append(f"\nAverage Response Times:")
            for source, avg_time in perf['avg_response_times_ms'].items():
                summary.append(f"  {source}: {avg_time:.2f}ms")

        summary.append("=" * 70)

        return "\n".join(summary)

    def save_metrics(self, filepath: str):
        """
        Save metrics to JSON file.

        Args:
            filepath: Path to save metrics file
        """
        try:
            metrics = self.get_metrics()

            with open(filepath, 'w') as f:
                json.dump(metrics, f, indent=2)

            logger.info(f"Metrics saved to {filepath}")

        except Exception as e:
            logger.error(f"Error saving metrics: {e}")

    def get_health_status(self) -> Dict:
        """
        Get health status of the price fetching system.

        Returns:
            Dictionary with health indicators
        """
        metrics = self.get_metrics()

        # Determine health based on metrics
        api_success_rate = metrics['api_calls']['success_rate_percent']
        cache_hit_rate = metrics['cache']['hit_rate_percent']
        error_count = metrics['errors']['total']
        total_calls = metrics['api_calls']['total']

        # Health thresholds
        health = "HEALTHY"
        issues = []

        if api_success_rate < 80 and total_calls > 10:
            health = "WARNING"
            issues.append(f"Low API success rate: {api_success_rate:.1f}%")

        if api_success_rate < 50 and total_calls > 10:
            health = "CRITICAL"

        if error_count > total_calls * 0.5 and total_calls > 10:
            health = "WARNING"
            issues.append(f"High error rate: {error_count} errors in {total_calls} calls")

        if cache_hit_rate < 20 and metrics['cache']['total_requests'] > 20:
            issues.append(f"Low cache hit rate: {cache_hit_rate:.1f}%")

        return {
            "status": health,
            "api_success_rate": api_success_rate,
            "cache_hit_rate": cache_hit_rate,
            "error_count": error_count,
            "total_api_calls": total_calls,
            "issues": issues,
            "timestamp": datetime.now().isoformat()
        }


# Global monitor instance
_monitor = PriceMonitor()


def get_monitor() -> PriceMonitor:
    """
    Get the global price monitor instance.

    Returns:
        Global PriceMonitor instance
    """
    return _monitor


def reset_monitor():
    """Reset the global monitor metrics."""
    _monitor.reset_metrics()


def get_metrics() -> Dict:
    """
    Get current monitoring metrics from global monitor.

    Returns:
        Dictionary containing all current metrics
    """
    return _monitor.get_metrics()


def get_summary() -> str:
    """
    Get human-readable summary from global monitor.

    Returns:
        Formatted summary string
    """
    return _monitor.get_summary()


def get_health_status() -> Dict:
    """
    Get health status from global monitor.

    Returns:
        Dictionary with health indicators
    """
    return _monitor.get_health_status()
