import sys

from pytest import main


def test_without_coverage():
    """Run tests without coverage."""
    sys.argv = ["pytest"] + sys.argv[1:]
    main()


def test_with_coverage():
    """Run tests with coverage and HTML report."""
    sys.argv = [
        "pytest",
        "--cov=world_builder",
        "--cov-report=html",
        "--cov-report=term-missing",
    ] + sys.argv[1:]
    main()


def test_with_ci_coverage():
    """Run tests with coverage and XML report for CI."""
    sys.argv = [
        "pytest",
        "--cov=world_builder",
        "--cov-report=xml",
        "--cov-report=term-missing",
    ] + sys.argv[1:]
    main()
