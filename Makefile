.PHONY: audit verify release-check status

audit:
	python scripts/audit_release_scope.py

verify:
	python scripts/audit_release_scope.py
	python scripts/verify_core_claims.py

release-check:
	python scripts/audit_release_scope.py --strict
	python scripts/verify_core_claims.py

status:
	@echo "Repository is in private pre-submission reconciliation."
	@echo "Run 'make verify' for current-stage checks."
	@echo "Run 'make release-check' only after full manifests, notebooks, and release SHA-256 manifest have been transferred."
