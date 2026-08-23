.PHONY: audit verify verify-pending verify-internal-predictions verify-pandian-predictions verify-tom2024 release-check status

audit:
	python scripts/audit_release_scope.py
	python scripts/audit_notebooks.py

verify:
	python scripts/audit_release_scope.py
	python scripts/audit_notebooks.py
	python scripts/verify_core_claims.py
	python scripts/verify_pending_transfer.py
	python scripts/verify_internal_predictions.py
	python scripts/verify_pandian_predictions.py
	python scripts/verify_tom2024_release.py

verify-pending:
	python scripts/verify_pending_transfer.py

verify-internal-predictions:
	python scripts/verify_internal_predictions.py

verify-pandian-predictions:
	python scripts/verify_pandian_predictions.py

verify-tom2024:
	python scripts/verify_tom2024_release.py

release-check:
	python scripts/audit_release_scope.py --strict
	python scripts/audit_notebooks.py --require
	python scripts/verify_core_claims.py
	python scripts/verify_pending_transfer.py --require-all
	python scripts/verify_internal_predictions.py --strict
	python scripts/verify_pandian_predictions.py --strict
	python scripts/verify_tom2024_release.py --strict

status:
	@echo "Repository is in private pre-submission reconciliation."
	@echo "Run 'make verify' for current-stage checks; missing prepared large/binary assets are reported as PENDING, not as failures."
	@echo "Run 'make release-check' only after the prepared core, E2-A, Pandian2019, TOM2024, and remaining external release assets plus the final repository-wide SHA-256 manifest have been transferred."
