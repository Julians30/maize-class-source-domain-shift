reference_index = architecture_names.index(reference_architecture)


difference_rows = []


for comparator_index, comparator in enumerate(architecture_names):
    if comparator == reference_architecture:
        continue
    differences = architecture_macro_f1[reference_index] - architecture_macro_f1[comparator_index]
    lower, upper = percentile_interval(differences)
    difference_rows.append({'comparator': comparator, 'difference': point_macro_f1[reference_index] - point_macro_f1[comparator_index], 'lower': lower, 'upper': upper})


difference_plot = pd.DataFrame(difference_rows).sort_values('difference').reset_index(drop=True)


figure, axis = plt.subplots(figsize=(9, 6))


positions = np.arange(len(difference_plot))


lower_error = difference_plot['difference'] - difference_plot['lower']


upper_error = difference_plot['upper'] - difference_plot['difference']


axis.errorbar(difference_plot['difference'], positions, xerr=np.vstack([lower_error, upper_error]), fmt='o', capsize=4)


axis.axvline(0.0, linestyle='--', linewidth=1)


axis.axvspan(-0.01, 0.01, alpha=0.12)


axis.set_yticks(positions)


axis.set_yticklabels(difference_plot['comparator'])


axis.set_xlabel('Macro-F1 difference: EfficientNet-B0 − comparator')


axis.set_ylabel('Comparator')


axis.set_title('Paired internal macro-F1 differences and 95% bootstrap intervals')


axis.grid(True, axis='x', alpha=0.3)


figure.tight_layout()


save_figure(figure, 'Figure_B_pairwise_differences_vs_EfficientNetB0')


class_matrix = class_intervals.pivot(index='architecture', columns='class_name', values='class_f1_mean').reindex(index=architecture_names, columns=EXPECTED_CLASSES)


figure, axis = plt.subplots(figsize=(13, 6))


image = axis.imshow(class_matrix.to_numpy(), aspect='auto')


axis.set_xticks(np.arange(len(EXPECTED_CLASSES)))


axis.set_xticklabels(EXPECTED_CLASSES, rotation=45, ha='right')


axis.set_yticks(np.arange(len(architecture_names)))


axis.set_yticklabels(architecture_names)


axis.set_xlabel('Operational class')


axis.set_ylabel('Architecture')


axis.set_title('Mean class-wise F1 across three seeds')


for row_index in range(class_matrix.shape[0]):
    for column_index in range(class_matrix.shape[1]):
        axis.text(column_index, row_index, f'{class_matrix.iloc[row_index, column_index]:.3f}', ha='center', va='center', fontsize=8)


figure.colorbar(image, ax=axis, label='Mean class-wise F1')


figure.tight_layout()


save_figure(figure, 'Figure_C_classwise_f1_heatmap')


calibration_plot = point_by_architecture.sort_values('accuracy_mean', ascending=True).reset_index(drop=True)


positions = np.arange(len(calibration_plot))


figure, axis = plt.subplots(figsize=(9, 6))


axis.scatter(calibration_plot['confidence_mean'], positions, label='Mean confidence', marker='o')


axis.scatter(calibration_plot['accuracy_mean'], positions, label='Observed accuracy', marker='s')


for position, row in calibration_plot.iterrows():
    axis.plot([row['confidence_mean'], row['accuracy_mean']], [position, position], linewidth=1)


axis.set_yticks(positions)


axis.set_yticklabels(calibration_plot['architecture'])


axis.set_xlabel('Proportion')


axis.set_ylabel('Architecture')


axis.set_title('Systematic internal underconfidence across architectures')


axis.legend()


axis.grid(True, axis='x', alpha=0.3)


figure.tight_layout()


save_figure(figure, 'Figure_D_confidence_accuracy_gap')


mean_risk_curves = risk_curves.groupby(['architecture', 'coverage']).agg(selective_risk=('selective_risk', 'mean')).reset_index()


figure, axis = plt.subplots(figsize=(9, 7))


for architecture in architecture_names:
    architecture_data = mean_risk_curves[mean_risk_curves['architecture'] == architecture]
    axis.plot(architecture_data['coverage'], architecture_data['selective_risk'], label=architecture)


axis.set_xlim(0.05, 1.0)


axis.set_xlabel('Coverage')


axis.set_ylabel('Error rate among retained predictions')


axis.set_title('Exact internal risk–coverage curves')


axis.legend(fontsize=8)


axis.grid(True, alpha=0.3)


figure.tight_layout()


save_figure(figure, 'Figure_E_exact_risk_coverage')


consensus_plot = consensus_by_class.sort_values('universally_correct_proportion').reset_index(drop=True)


figure, axis = plt.subplots(figsize=(10, 6))


positions = np.arange(len(consensus_plot))


axis.barh(positions, consensus_plot['universally_correct_proportion'])


axis.set_yticks(positions)


axis.set_yticklabels(consensus_plot['class_name'])


axis.set_xlabel('Proportion classified correctly by all 18 runs')


axis.set_ylabel('Operational class')


axis.set_title('Cross-architecture consensus in internal correctness')


axis.grid(True, axis='x', alpha=0.3)


figure.tight_layout()


save_figure(figure, 'Figure_F_consensus_difficulty_by_class')


figure, axis = plt.subplots(figsize=(8, 7))


for architecture in architecture_names:
    architecture_data = reliability_summary[reliability_summary['architecture'] == architecture]
    axis.plot(architecture_data['mean_confidence'], architecture_data['observed_accuracy'], marker='o', label=architecture)


axis.plot([0.0, 1.0], [0.0, 1.0], linestyle='--', linewidth=1)


axis.set_xlabel('Mean confidence')


axis.set_ylabel('Observed accuracy')


axis.set_title('Equal-frequency reliability curves')


axis.legend(fontsize=8)


axis.grid(True, alpha=0.3)


figure.tight_layout()


save_figure(figure, 'Figure_G_equal_frequency_reliability')


best_macro_f1 = architecture_intervals.iloc[0]


most_stable = point_by_architecture.loc[point_by_architecture['macro_f1_sd'].idxmin()]


lowest_aurc = risk_summary.loc[risk_summary['aurc_mean'].idxmin()]


lowest_consensus = consensus_by_class.loc[consensus_by_class['universally_correct_proportion'].idxmin()]
