PYTHON ?= python3

.PHONY: validate validate-release validate-claude

validate:
	$(PYTHON) scripts/validate.py

validate-release:
	$(PYTHON) scripts/validate.py --release

validate-claude:
	claude plugin validate --strict plugins/aburasashi
	claude plugin validate --strict .
