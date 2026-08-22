.PHONY: audit verify verify-pending verify-internal-predictions release-check status

audit:
	python scripts/audit_release_scope.py
	python scripts/audit_notebooks.py

verify:
	python scripts/audit_release_scope.py
	python scripts/audit_notebooks.py
	python scripts/verify_core_claims.py
	python scripts/verify_pending_transfer.py
	python scripts/verify_internal_predictions.py

verify-pending:
	python scripts/verify_pending_transfer.py

verify-internal-predictions:
	python scripts/verify_internal_predictions.py

release-check:
	python scripts/audit_release_scope.py --strict
	python scripts/audit_notebooks.py --require
	python scripts/verify_core_claims.py
	python scripts/verify_pending_transfer.py --require-all
	python scripts/verify_internal_predictions.py --strict

status:
	@echo "Repository is in private pre-submission reconciliation."
	@echo "Run 'make verify' for current-stage checks; missing prepared large/binary assets are reported as PENDING, not as failures."
	@echo "Run 'make release-check' only after the pending transfer assets, all 18 release-safe E2-A internal prediction files, and final release SHA-256 manifest have been transferred."
