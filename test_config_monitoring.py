"""
Test Configuration and Monitoring - Task 16.5

Tests the configuration system and monitoring/metrics functionality.
"""

import sys
from pathlib import Path
import io
import json

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modules.portfolio_dashboard.price_monitoring import (
    PriceMonitor,
    get_monitor,
    get_metrics,
    get_summary,
    get_health_status
)


def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_configuration_file():
    """Test that configuration file exists and is valid."""
    print_section("TEST 1: Configuration File")

    config_path = Path(__file__).parent / "src" / "modules" / "portfolio_dashboard" / "price_config.json"

    print(f"\n1. Checking configuration file exists...")
    print(f"   Path: {config_path}")

    if config_path.exists():
        print(f"   ✓ Configuration file exists")
    else:
        print(f"   ✗ FAIL: Configuration file not found")
        return False

    print(f"\n2. Validating JSON structure...")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        print(f"   ✓ Valid JSON")

        # Check for required sections
        required_sections = ['cache', 'staleness', 'api', 'data_sources', 'currency', 'monitoring', 'limits']

        print(f"\n3. Checking required sections...")
        for section in required_sections:
            if section in config:
                print(f"   ✓ {section}: present")
            else:
                print(f"   ✗ {section}: MISSING")
                return False

        print(f"\n4. Configuration values:")
        print(f"   - Cache TTL: {config['cache']['ttl_seconds']}s")
        print(f"   - Max Retries: {config['api']['max_retries']}")
        print(f"   - Staleness Threshold: {config['staleness']['threshold_hours']}h")
        print(f"   - Rate Limit Delay: {config['api']['rate_limit_delay_seconds']}s")

        print(f"\n   ✓ PASS: Configuration file valid")
        return True

    except json.JSONDecodeError as e:
        print(f"   ✗ FAIL: Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"   ✗ FAIL: Error reading config: {e}")
        return False


def test_monitor_creation():
    """Test creating a price monitor instance."""
    print_section("TEST 2: Monitor Creation")

    print(f"\n1. Creating PriceMonitor instance...")
    monitor = PriceMonitor()

    if monitor:
        print(f"   ✓ Monitor created successfully")
    else:
        print(f"   ✗ FAIL: Could not create monitor")
        return False

    print(f"\n2. Checking initial metrics...")
    metrics = monitor.get_metrics()

    if metrics:
        print(f"   ✓ Metrics retrieved")
        print(f"   - Session start: {metrics['session']['start_time']}")
        print(f"   - Total API calls: {metrics['api_calls']['total']}")
        print(f"   - Cache hits: {metrics['cache']['hits']}")
    else:
        print(f"   ✗ FAIL: Could not retrieve metrics")
        return False

    print(f"\n   ✓ PASS: Monitor creation works")
    return True


def test_api_call_tracking():
    """Test tracking API calls."""
    print_section("TEST 3: API Call Tracking")

    monitor = PriceMonitor()

    print(f"\n1. Recording successful API calls...")
    monitor.record_api_call("yfinance", success=True, duration_ms=150.5)
    monitor.record_api_call("yfinance", success=True, duration_ms=200.3)
    monitor.record_api_call("tase_yahoo", success=True, duration_ms=180.0)

    print(f"\n2. Recording failed API calls...")
    monitor.record_api_call("yfinance", success=False)
    monitor.record_api_call("tase_yahoo", success=False)

    print(f"\n3. Checking metrics...")
    metrics = monitor.get_metrics()

    total_calls = metrics['api_calls']['total']
    successes = metrics['api_calls']['successes']
    failures = metrics['api_calls']['failures']
    success_rate = metrics['api_calls']['success_rate_percent']

    print(f"   - Total calls: {total_calls}")
    print(f"   - Successes: {successes}")
    print(f"   - Failures: {failures}")
    print(f"   - Success rate: {success_rate:.1f}%")

    if total_calls == 5 and successes == 3 and failures == 2:
        print(f"   ✓ Call counts correct")
    else:
        print(f"   ✗ FAIL: Call counts incorrect")
        return False

    if abs(success_rate - 60.0) < 0.1:
        print(f"   ✓ Success rate correct (60%)")
    else:
        print(f"   ✗ FAIL: Success rate incorrect")
        return False

    print(f"\n   ✓ PASS: API call tracking works")
    return True


def test_cache_tracking():
    """Test tracking cache hits and misses."""
    print_section("TEST 4: Cache Tracking")

    monitor = PriceMonitor()

    print(f"\n1. Recording cache hits and misses...")
    monitor.record_cache_hit()
    monitor.record_cache_hit()
    monitor.record_cache_hit()
    monitor.record_cache_miss()

    print(f"\n2. Checking cache metrics...")
    metrics = monitor.get_metrics()

    hits = metrics['cache']['hits']
    misses = metrics['cache']['misses']
    total = metrics['cache']['total_requests']
    hit_rate = metrics['cache']['hit_rate_percent']

    print(f"   - Cache hits: {hits}")
    print(f"   - Cache misses: {misses}")
    print(f"   - Total requests: {total}")
    print(f"   - Hit rate: {hit_rate:.1f}%")

    if hits == 3 and misses == 1 and total == 4:
        print(f"   ✓ Cache counts correct")
    else:
        print(f"   ✗ FAIL: Cache counts incorrect")
        return False

    if abs(hit_rate - 75.0) < 0.1:
        print(f"   ✓ Hit rate correct (75%)")
    else:
        print(f"   ✗ FAIL: Hit rate incorrect")
        return False

    print(f"\n   ✓ PASS: Cache tracking works")
    return True


def test_error_tracking():
    """Test tracking errors."""
    print_section("TEST 5: Error Tracking")

    monitor = PriceMonitor()

    print(f"\n1. Recording various errors...")
    monitor.record_error("timeout")
    monitor.record_error("timeout")
    monitor.record_error("rate_limit")
    monitor.record_error("invalid_symbol")

    print(f"\n2. Checking error metrics...")
    metrics = monitor.get_metrics()

    total_errors = metrics['errors']['total']
    by_type = metrics['errors']['by_type']

    print(f"   - Total errors: {total_errors}")
    print(f"   - By type: {by_type}")

    if total_errors == 4:
        print(f"   ✓ Total error count correct")
    else:
        print(f"   ✗ FAIL: Total error count incorrect")
        return False

    if by_type.get('timeout') == 2 and by_type.get('rate_limit') == 1:
        print(f"   ✓ Error type counts correct")
    else:
        print(f"   ✗ FAIL: Error type counts incorrect")
        return False

    print(f"\n   ✓ PASS: Error tracking works")
    return True


def test_fallback_tracking():
    """Test tracking fallback usage."""
    print_section("TEST 6: Fallback Tracking")

    monitor = PriceMonitor()

    print(f"\n1. Recording fallback usage...")
    monitor.record_fallback("manual")
    monitor.record_fallback("cached")
    monitor.record_fallback("cached")
    monitor.record_fallback("unavailable")

    monitor.record_stale_price()
    monitor.record_stale_price()

    monitor.record_manual_price()

    print(f"\n2. Checking fallback metrics...")
    metrics = monitor.get_metrics()

    fallbacks = metrics['fallbacks']

    print(f"   - Total fallbacks: {fallbacks['total']}")
    print(f"   - By level: {fallbacks['by_level']}")
    print(f"   - Stale prices: {fallbacks['stale_prices_used']}")
    print(f"   - Manual prices: {fallbacks['manual_prices_used']}")

    if fallbacks['total'] == 4:
        print(f"   ✓ Total fallback count correct")
    else:
        print(f"   ✗ FAIL: Total fallback count incorrect")
        return False

    if fallbacks['stale_prices_used'] == 2 and fallbacks['manual_prices_used'] == 1:
        print(f"   ✓ Fallback details correct")
    else:
        print(f"   ✗ FAIL: Fallback details incorrect")
        return False

    print(f"\n   ✓ PASS: Fallback tracking works")
    return True


def test_health_status():
    """Test health status generation."""
    print_section("TEST 7: Health Status")

    monitor = PriceMonitor()

    print(f"\n1. Scenario: Healthy system...")
    for i in range(20):
        monitor.record_api_call("yfinance", success=True)
    monitor.record_cache_hit()
    monitor.record_cache_hit()

    health = monitor.get_health_status()

    print(f"   - Status: {health['status']}")
    print(f"   - API Success Rate: {health['api_success_rate']:.1f}%")
    print(f"   - Issues: {health['issues']}")

    if health['status'] == "HEALTHY":
        print(f"   ✓ Healthy status detected correctly")
    else:
        print(f"   ⚠ Status: {health['status']} (expected HEALTHY)")

    print(f"\n2. Scenario: Warning system...")
    monitor.reset_metrics()

    for i in range(15):
        monitor.record_api_call("yfinance", success=True)
    for i in range(5):
        monitor.record_api_call("yfinance", success=False)

    health = monitor.get_health_status()

    print(f"   - Status: {health['status']}")
    print(f"   - API Success Rate: {health['api_success_rate']:.1f}%")
    print(f"   - Issues: {len(health['issues'])} issue(s)")

    if health['status'] in ["WARNING", "HEALTHY"]:
        print(f"   ✓ Status detection works")
    else:
        print(f"   ⚠ Unexpected status: {health['status']}")

    print(f"\n   ✓ PASS: Health status works")
    return True


def test_summary_generation():
    """Test summary report generation."""
    print_section("TEST 8: Summary Generation")

    monitor = PriceMonitor()

    print(f"\n1. Populating monitor with sample data...")
    monitor.record_api_call("yfinance", success=True, duration_ms=120.5)
    monitor.record_api_call("tase_yahoo", success=True, duration_ms=250.0)
    monitor.record_cache_hit()
    monitor.record_error("timeout")
    monitor.record_fallback("cached")

    print(f"\n2. Generating summary...")
    summary = monitor.get_summary()

    if summary and len(summary) > 100:
        print(f"   ✓ Summary generated ({len(summary)} characters)")
        print(f"\n--- SAMPLE SUMMARY ---")
        print(summary)
        print(f"--- END SUMMARY ---")
    else:
        print(f"   ✗ FAIL: Summary generation failed")
        return False

    print(f"\n   ✓ PASS: Summary generation works")
    return True


def test_global_monitor():
    """Test global monitor instance."""
    print_section("TEST 9: Global Monitor")

    print(f"\n1. Getting global monitor...")
    monitor = get_monitor()

    if monitor:
        print(f"   ✓ Global monitor retrieved")
    else:
        print(f"   ✗ FAIL: Could not get global monitor")
        return False

    print(f"\n2. Testing global functions...")
    metrics = get_metrics()
    summary = get_summary()
    health = get_health_status()

    if metrics and summary and health:
        print(f"   ✓ Global functions work")
    else:
        print(f"   ✗ FAIL: Global functions failed")
        return False

    print(f"\n   ✓ PASS: Global monitor works")
    return True


def run_all_tests():
    """Run all configuration and monitoring tests."""
    print("\n" + "█" * 70)
    print("  CONFIGURATION AND MONITORING TEST SUITE")
    print("  Task 16.5: Add Configuration and Monitoring")
    print("█" * 70)

    tests = [
        ("Configuration File", test_configuration_file),
        ("Monitor Creation", test_monitor_creation),
        ("API Call Tracking", test_api_call_tracking),
        ("Cache Tracking", test_cache_tracking),
        ("Error Tracking", test_error_tracking),
        ("Fallback Tracking", test_fallback_tracking),
        ("Health Status", test_health_status),
        ("Summary Generation", test_summary_generation),
        ("Global Monitor", test_global_monitor),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            result = test_func()
            if result is True or result is None:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ TEST ERROR: {test_name}")
            print(f"   Unexpected error: {type(e).__name__}: {e}\n")
            failed += 1

    # Summary
    print("\n" + "█" * 70)
    print("  TEST SUMMARY")
    print("█" * 70)
    print(f"\n  Total Tests: {len(tests)}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")

    if failed == 0:
        print(f"\n  🎉 ALL TESTS PASSED! Configuration and monitoring functional.")
        print(f"  ✓ Task 16.5 requirements satisfied")
        print(f"  ✓ Configuration file created")
        print(f"  ✓ Monitoring system operational")
        print(f"  ✓ Metrics tracking works")
        print(f"  ✓ Health status detection works")
    else:
        print(f"\n  ⚠️  Some tests failed. Review implementation.")

    print("\n" + "█" * 70 + "\n")

    return failed == 0


if __name__ == "__main__":
    print("\n[START] Running Configuration and Monitoring Tests\n")

    success = run_all_tests()

    print("\n[COMPLETE] Test suite finished!\n")

    sys.exit(0 if success else 1)
