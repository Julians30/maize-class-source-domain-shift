.PHONY: audit verify verify-pending release-check status

audit:
	python scripts/audit_release_scope.py

verify:
	python scripts/audit_release_scope.py
	python scripts/verify_core_claims.py
	python scripts/verify_pending_transfer.py

verify-pending:
	python scripts/verify_pending_transfer.py

release-check:
	python scripts/audit_release_scope.py --strict
	python scripts/verify_core_claims.py
	python scripts/verify_pending_transfer.py --require-all

status:
	@echo "Repository is in private pre-submission reconciliation."
	@echo "Run 'make verify' for current-stage checks; missing prepared large/binary assets are reported as PENDING, not as failures."
	@echo "Run 'make release-check' only after the pending transfer assets and final release SHA-256 manifest have been transferred."
