summary = {'validated_runs': 18, 'internal_test_images': EXPECTED_N, 'bootstrap_replicates': N_BOOTSTRAP, 'best_mean_macro_f1_architecture': best_macro_f1['architecture'], 'best_mean_macro_f1': float(best_macro_f1['macro_f1_mean']), 'best_mean_macro_f1_ci95': [float(best_macro_f1['bootstrap_ci95_lower']), float(best_macro_f1['bootstrap_ci95_upper'])], 'significant_pairwise_macro_f1_comparisons_after_holm': int(pairwise['significant_after_holm'].sum()), 'most_stable_architecture_by_macro_f1_sd': most_stable['architecture'], 'most_stable_macro_f1_sd': float(most_stable['macro_f1_sd']), 'lowest_mean_aurc_architecture': lowest_aurc['architecture'], 'lowest_mean_aurc': float(lowest_aurc['aurc_mean']), 'hardest_class_by_universal_correctness': lowest_consensus['class_name'], 'hardest_class_universally_correct_proportion': float(lowest_consensus['universally_correct_proportion']), 'six_architecture_ensemble_macro_f1': float(six_architecture_ensemble_point), 'eighteen_model_ensemble_macro_f1': float(all_model_point)}


summary_path = OUTPUT_DIR / 'MANUSCRIPT_final_inference_summary.json'


summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')


print(json.dumps(summary, indent=2, ensure_ascii=False))


zip_path = OUTPUT_DIR.parent / 'final_paired_inference_reproduction_outputs.zip'


if zip_path.exists():
    zip_path.unlink()


with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in OUTPUT_DIR.rglob('*'):
        if path.is_file():
            archive.write(path, arcname=path.relative_to(OUTPUT_DIR))


print('Completed successfully.')


print('Output folder:', OUTPUT_DIR)


print('Reproduction ZIP:', zip_path)
