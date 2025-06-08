import sys

from pytest import main


def test_without_coverage():
    sys.argv = ["pytest"] + sys.argv[1:]
    main()


def test_with_coverage():
    sys.argv = [
        "pytest",
        "--cov=world_builder",
        "--cov-report=html",
        "--cov-report=term-missing",
    ] + sys.argv[1:]
    main()
