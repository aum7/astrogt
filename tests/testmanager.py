import unittest
import sys

# import os
import logging
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("testmanager")


class TestManager:
    """Manages test execution for astrogt"""

    def __init__(self):
        self.test_suites = []

    def add_test_suite(self, test_suite):
        """Add a test suite to the manager"""
        self.test_suites.append(test_suite)

    def discover_tests(self, start_dir="tests", pattern="test_*.py"):
        """Discover tests in the specified directory"""
        loader = unittest.TestLoader()
        discovered_tests = loader.discover(start_dir, pattern=pattern)
        self.test_suites.append(discovered_tests)

    def run_tests(self, verbosity=2):
        """Run all registered test suites"""
        logger.info(
            f"Starting test run at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )

        runner = unittest.TextTestRunner(verbosity=verbosity)
        results = []

        for test_suite in self.test_suites:
            logger.info(f"Running test suite: {test_suite}")
            result = runner.run(test_suite)
            results.append(result)

        total_tests = sum(result.testsRun for result in results)
        total_failures = sum(len(result.failures) for result in results)
        total_errors = sum(len(result.errors) for result in results)

        logger.info(
            f"Test run completed: {total_tests} tests, {total_failures} failures, {total_errors} errors"
        )

        return all(result.wasSuccessful() for result in results)


# Command-line execution
if __name__ == "__main__":
    manager = TestManager()
    manager.discover_tests()
    success = manager.run_tests()
    sys.exit(0 if success else 1)
