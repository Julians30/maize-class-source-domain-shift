for bootstrap_index in range(N_BOOTSTRAP):
    confusion = np.bincount(N_CLASSES * bootstrap_true[bootstrap_index] + all_model_prediction[bootstrap_indices[bootstrap_index]], minlength=N_CLASSES * N_CLASSES).reshape(N_CLASSES, N_CLASSES)
    all_model_bootstrap[bootstrap_index] = metrics_from_confusion(confusion)['macro_f1']


all_model_point = f1_score(y_true, all_model_prediction, average='macro')


ensemble_rows = []


for name, point_value, bootstrap_values in [('Six-architecture soft vote averaged across seeds', six_architecture_ensemble_point, six_architecture_ensemble_bootstrap), ('Eighteen-model soft vote', all_model_point, all_model_bootstrap)]:
    lower, upper = percentile_interval(bootstrap_values)
    ensemble_rows.append({'ensemble': name, 'macro_f1': point_value, 'bootstrap_ci95_lower': lower, 'bootstrap_ci95_upper': upper})


ensemble_intervals = pd.DataFrame(ensemble_rows)


ensemble_intervals.to_csv(OUTPUT_DIR / '07_ensemble_bootstrap_intervals.csv', index=False, encoding='utf-8-sig')


ensemble_comparison_rows = []


for architecture_index, architecture in enumerate(architecture_names):
    differences = six_architecture_ensemble_bootstrap - architecture_macro_f1[architecture_index]
    lower, upper = percentile_interval(differences)
    ensemble_comparison_rows.append({'ensemble': 'Six-architecture soft vote averaged across seeds', 'comparator': architecture, 'macro_f1_difference': six_architecture_ensemble_point - point_macro_f1[architecture_index], 'bootstrap_ci95_lower': lower, 'bootstrap_ci95_upper': upper, 'bootstrap_raw_p': bootstrap_two_sided_p(differences)})


ensemble_comparisons = pd.DataFrame(ensemble_comparison_rows)


ensemble_comparisons['holm_p'] = holm_adjust(ensemble_comparisons['bootstrap_raw_p'].to_numpy())


ensemble_comparisons['significant_after_holm'] = ensemble_comparisons['holm_p'] < 0.05


ensemble_comparisons.to_csv(OUTPUT_DIR / '08_ensemble_vs_architectures_bootstrap.csv', index=False, encoding='utf-8-sig')


display(ensemble_intervals)


display(ensemble_comparisons)


risk_rows = []


risk_curve_rows = []


for run_index, (architecture, seed) in enumerate(run_names):
    correct = predictions[run_index] == y_true
    aurc, coverage, risk = exact_aurc(correct, confidences[run_index])
    row = {'architecture': architecture, 'seed': seed, 'aurc': aurc}
    for requested_coverage in [0.5, 0.8, 0.9, 0.95, 1.0]:
        location = min(len(coverage) - 1, max(0, int(math.ceil(requested_coverage * len(coverage))) - 1))
        row[f'risk_at_{requested_coverage:.2f}_coverage'] = float(risk[location])
    risk_rows.append(row)
    selected_locations = np.unique(np.linspace(0, len(coverage) - 1, 300, dtype=int))
    for location in selected_locations:
        risk_curve_rows.append({'architecture': architecture, 'seed': seed, 'coverage': coverage[location], 'selective_risk': risk[location]})


risk_by_run = pd.DataFrame(risk_rows)


risk_by_run.to_csv(OUTPUT_DIR / '09_exact_aurc_and_risk_by_run.csv', index=False, encoding='utf-8-sig')


risk_summary = risk_by_run.groupby('architecture').agg(aurc_mean=('aurc', 'mean'), aurc_sd=('aurc', 'std'), risk_50_mean=('risk_at_0.50_coverage', 'mean'), risk_80_mean=('risk_at_0.80_coverage', 'mean'), risk_90_mean=('risk_at_0.90_coverage', 'mean'), risk_95_mean=('risk_at_0.95_coverage', 'mean'), risk_100_mean=('risk_at_1.00_coverage', 'mean')).reset_index()


risk_summary.to_csv(OUTPUT_DIR / '10_exact_aurc_summary.csv', index=False, encoding='utf-8-sig')


risk_curves = pd.DataFrame(risk_curve_rows)


risk_curves.to_csv(OUTPUT_DIR / '11_exact_risk_coverage_coordinates.csv', index=False, encoding='utf-8-sig')


display(risk_summary.sort_values('aurc_mean'))


reliability_rows = []


for run_index, (architecture, seed) in enumerate(run_names):
    correct = predictions[run_index] == y_true
    reliability = equal_frequency_reliability(correct, confidences[run_index], n_bins=10)
    reliability['architecture'] = architecture
    reliability['seed'] = seed
    reliability_rows.append(reliability)


reliability_by_run = pd.concat(reliability_rows, ignore_index=True)


reliability_by_run.to_csv(OUTPUT_DIR / '12_equal_frequency_reliability_by_run.csv', index=False, encoding='utf-8-sig')


reliability_summary = reliability_by_run.groupby(['architecture', 'bin']).agg(n_mean=('n', 'mean'), mean_confidence=('mean_confidence', 'mean'), observed_accuracy=('observed_accuracy', 'mean')).reset_index()


reliability_summary.to_csv(OUTPUT_DIR / '13_equal_frequency_reliability_summary.csv', index=False, encoding='utf-8-sig')


display(reliability_summary.head(20))


correct_matrix = predictions == y_true[None, :]


number_correct_runs = correct_matrix.sum(axis=0)


consensus_rows = []


for class_index, class_name in enumerate(EXPECTED_CLASSES):
    mask = y_true == class_index
    class_counts = number_correct_runs[mask]
    consensus_rows.append({'class_name': class_name, 'support': int(mask.sum()), 'universally_correct_images': int(np.sum(class_counts == len(run_names))), 'universally_correct_proportion': float(np.mean(class_counts == len(run_names))), 'universally_wrong_images': int(np.sum(class_counts == 0)), 'universally_wrong_proportion': float(np.mean(class_counts == 0)), 'mean_correct_runs_out_of_18': float(class_counts.mean()), 'median_correct_runs_out_of_18': float(np.median(class_counts))})


consensus_by_class = pd.DataFrame(consensus_rows)


consensus_by_class.to_csv(OUTPUT_DIR / '14_consensus_difficulty_by_class.csv', index=False, encoding='utf-8-sig')


display(consensus_by_class.sort_values('universally_correct_proportion'))


plot_data = architecture_intervals.sort_values('macro_f1_mean').reset_index(drop=True)


figure, axis = plt.subplots(figsize=(9, 6))


positions = np.arange(len(plot_data))


lower_error = plot_data['macro_f1_mean'] - plot_data['bootstrap_ci95_lower']


upper_error = plot_data['bootstrap_ci95_upper'] - plot_data['macro_f1_mean']


axis.errorbar(plot_data['macro_f1_mean'], positions, xerr=np.vstack([lower_error, upper_error]), fmt='o', capsize=4)


axis.set_yticks(positions)


axis.set_yticklabels(plot_data['architecture'])


axis.set_xlabel('Mean internal macro-F1')


axis.set_ylabel('Architecture')


axis.set_title('Internal macro-F1 with class-stratified bootstrap intervals')


axis.grid(True, axis='x', alpha=0.3)


figure.tight_layout()


save_figure(figure, 'Figure_A_macro_f1_bootstrap_intervals')


reference_architecture = 'EfficientNet-B0'
