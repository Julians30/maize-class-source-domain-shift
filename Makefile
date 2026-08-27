.PHONY: audit verify verify-canonical verify-provenance verify-pending verify-internal-blocked verify-ranking verify-supplementary verify-internal-predictions verify-pandian-predictions verify-plantvillage verify-tom2024 release-manifest verify-release-manifest release-check status

verify-canonical:
	python scripts/verify_canonical_analysis_code.py

verify-provenance:
	python scripts/verify_provenance_analysis_code.py

audit:
	python scripts/verify_canonical_analysis_code.py
	python scripts/verify_provenance_analysis_code.py
	python scripts/audit_release_scope.py
	python scripts/audit_notebooks.py --require

verify:
	python scripts/verify_canonical_analysis_code.py
	python scripts/verify_provenance_analysis_code.py
	python scripts/audit_release_scope.py
	python scripts/audit_notebooks.py --require
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
	python scripts/verify_canonical_analysis_code.py
	python scripts/verify_provenance_analysis_code.py
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
	@echo "Repository is private and in pre-submission reproducibility hardening."
	@echo "Run 'make verify' for current-stage checks."
	@echo "Use 'make release-check' only after every final registered release asset and release_sha256.csv are committed."
