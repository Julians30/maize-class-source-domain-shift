.PHONY: audit verify verify-pending verify-internal-blocked verify-ranking verify-supplementary verify-internal-predictions verify-pandian-predictions verify-plantvillage verify-tom2024 release-manifest verify-release-manifest release-check status

audit:
	python scripts/audit_release_scope.py
	python scripts/audit_notebooks.py

verify:
	python scripts/audit_release_scope.py
	python scripts/audit_notebooks.py
	python scripts/verify_core_claims.py
	python scripts/verify_internal_blocked_exact.py
	python scripts/verify_ranking_stability.py
	python scripts/verify_supplementary_reconciliation.py
	python scripts/verify_pending_transfer.py
	python scripts/verify_internal_predictions.py
	python scripts/verify_pandian_predictions.py
	python scripts/verify_plantvillage_release.py
	python scripts/verify_tom2024_release.py

verify-pending:
	python scripts/verify_pending_transfer.py

verify-internal-blocked:
	python scripts/verify_internal_blocked_exact.py

verify-ranking:
	python scripts/verify_ranking_stability.py

verify-supplementary:
	python scripts/verify_supplementary_reconciliation.py

verify-internal-predictions:
	python scripts/verify_internal_predictions.py

verify-pandian-predictions:
	python scripts/verify_pandian_predictions.py

verify-plantvillage:
	python scripts/verify_plantvillage_release.py

verify-tom2024:
	python scripts/verify_tom2024_release.py

release-manifest:
	python scripts/build_release_manifest.py

verify-release-manifest:
	python scripts/verify_release_manifest.py

release-check:
	python scripts/audit_release_scope.py --strict
	python scripts/audit_notebooks.py --require
	python scripts/verify_core_claims.py
	python scripts/verify_internal_blocked_exact.py
	python scripts/verify_ranking_stability.py
	python scripts/verify_supplementary_reconciliation.py --strict
	python scripts/verify_pending_transfer.py --require-all
	python scripts/verify_internal_predictions.py --strict
	python scripts/verify_pandian_predictions.py --strict
	python scripts/verify_plantvillage_release.py --strict
	python scripts/verify_tom2024_release.py --strict
	python scripts/verify_release_manifest.py

status:
	@echo "Repository is in private pre-submission reconciliation."
	@echo "Run 'make verify' for current-stage checks; missing prepared large/binary assets are reported as PENDING, not as failures."
	@echo "After all final assets are committed and the tree is clean, run 'make release-manifest', commit manifests/release_sha256.csv, then run 'make release-check'."
