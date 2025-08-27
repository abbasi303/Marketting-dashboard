# Run pytest with coverage for the marketing dashboard app
pytest --cov=app --cov-report=xml --cov-report=html --cov-report=term-missing --cov-fail-under=95 tests/
