.PHONY: audit verify verify-canonical verify-provenance verify-external-registry presubmission-check verify-pending verify-internal-blocked verify-ranking verify-supplementary verify-internal-predictions verify-pandian-predictions verify-plantvillage verify-tom2024 release-manifest verify-release-manifest release-check status

verify-canonical:
	python scripts/verify_canonical_analysis_code.py

verify-provenance:
	python scripts/verify_provenance_analysis_code.py

verify-external-registry:
	python scripts/verify_external_artifact_registry.py --presubmission

audit:
	python scripts/verify_canonical_analysis_code.py
	python scripts/verify_provenance_analysis_code.py
	python scripts/audit_release_scope.py
	python scripts/audit_notebooks.py --require
	python scripts/verify_external_artifact_registry.py --presubmission

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
	python scripts/verify_external_artifact_registry.py --presubmission

presubmission-check:
	python -m compileall -q scripts -x 'scripts/analysis/provenance_fragments/.*'
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
	python scripts/verify_external_artifact_registry.py --presubmission

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
	python scripts/verify_external_artifact_registry.py --release
	python scripts/verify_release_manifest.py

status:
	@echo "Repository is private and pre-submission reproducibility hardening is complete only when 'make presubmission-check' passes."
	@echo "Use 'make release-check' only at manuscript-submission/public-archive time."
