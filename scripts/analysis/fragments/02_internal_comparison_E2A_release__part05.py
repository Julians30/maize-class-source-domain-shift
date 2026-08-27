for architecture in architecture_order:
    seed_macro_curves = []
    for seed in SEEDS:
        df = runs[architecture, seed]
        probabilities = df[probability_columns(df)].to_numpy(dtype=float)
        y_true = df['true_idx'].to_numpy(dtype=int)
        class_curves = []
        for class_idx in range(len(EXPECTED_CLASSES)):
            binary_true = (y_true == class_idx).astype(int)
            fpr, tpr, _ = roc_curve(binary_true, probabilities[:, class_idx])
            interpolated = np.interp(common_fpr, fpr, tpr)
            interpolated[0] = 0.0
            class_curves.append(interpolated)
        seed_macro_curves.append(np.mean(class_curves, axis=0))
    mean_curve = np.mean(seed_macro_curves, axis=0)
    mean_curve[-1] = 1.0
    mean_auc = global_summary.set_index('architecture').loc[architecture, 'roc_auc_macro_mean']
    ax.plot(common_fpr, mean_curve, label=f'{architecture} (AUC={mean_auc:.3f})')
    for fpr_value, tpr_value in zip(common_fpr, mean_curve):
        roc_rows.append({'architecture': architecture, 'false_positive_rate': fpr_value, 'mean_macro_true_positive_rate': tpr_value})


ax.plot([0, 1], [0, 1], linestyle='--', linewidth=1)


ax.set_xlabel('False-positive rate')


ax.set_ylabel('Mean one-vs-rest true-positive rate')


ax.set_title('Mean macro ROC curves across three seeds')


ax.legend(fontsize=8)


ax.grid(True, alpha=0.3)


fig.tight_layout()


save_figure(fig, 'Figure_macro_ROC_all_architectures')


pd.DataFrame(roc_rows).to_csv(OUTPUT_DIR / '11_macro_roc_curve_coordinates.csv', index=False, encoding='utf-8-sig')


common_recall = np.linspace(0.0, 1.0, 1001)


pr_rows = []


fig, ax = plt.subplots(figsize=(8, 7))


for architecture in architecture_order:
    seed_macro_curves = []
    for seed in SEEDS:
        df = runs[architecture, seed]
        probabilities = df[probability_columns(df)].to_numpy(dtype=float)
        y_true = df['true_idx'].to_numpy(dtype=int)
        class_curves = []
        for class_idx in range(len(EXPECTED_CLASSES)):
            binary_true = (y_true == class_idx).astype(int)
            precision, recall, _ = precision_recall_curve(binary_true, probabilities[:, class_idx])
            order = np.argsort(recall)
            recall_sorted = recall[order]
            precision_sorted = precision[order]
            interpolated = np.interp(common_recall, recall_sorted, precision_sorted)
            class_curves.append(interpolated)
        seed_macro_curves.append(np.mean(class_curves, axis=0))
    mean_curve = np.mean(seed_macro_curves, axis=0)
    mean_ap = global_summary.set_index('architecture').loc[architecture, 'average_precision_macro_mean']
    ax.plot(common_recall, mean_curve, label=f'{architecture} (AP={mean_ap:.3f})')
    for recall_value, precision_value in zip(common_recall, mean_curve):
        pr_rows.append({'architecture': architecture, 'recall': recall_value, 'mean_macro_precision': precision_value})


ax.set_xlabel('Recall')


ax.set_ylabel('Mean one-vs-rest precision')


ax.set_title('Mean macro precision–recall curves across three seeds')


ax.legend(fontsize=8)


ax.grid(True, alpha=0.3)


fig.tight_layout()


save_figure(fig, 'Figure_macro_precision_recall_all_architectures')


pd.DataFrame(pr_rows).to_csv(OUTPUT_DIR / '12_macro_precision_recall_coordinates.csv', index=False, encoding='utf-8-sig')


reliability_summary = reliability_all.groupby(['architecture', 'bin']).agg(n_mean=('n', 'mean'), mean_confidence=('mean_confidence', 'mean'), accuracy=('accuracy', 'mean')).reset_index()


reliability_summary.to_csv(OUTPUT_DIR / '13_reliability_summary_by_architecture.csv', index=False, encoding='utf-8-sig')


fig, ax = plt.subplots(figsize=(8, 7))


for architecture in architecture_order:
    part = reliability_summary[reliability_summary['architecture'] == architecture].dropna(subset=['mean_confidence', 'accuracy'])
    ax.plot(part['mean_confidence'], part['accuracy'], marker='o', label=architecture)


ax.plot([0, 1], [0, 1], linestyle='--', linewidth=1)


ax.set_xlabel('Mean confidence')


ax.set_ylabel('Observed accuracy')


ax.set_title('Internal reliability curves')


ax.legend(fontsize=8)


ax.grid(True, alpha=0.3)


fig.tight_layout()


save_figure(fig, 'Figure_reliability_all_architectures')


coverage_grid = np.array([0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.975, 1.0])


selective_rows = []


for (architecture, seed), df in runs.items():
    confidence = df['confidence'].to_numpy(dtype=float)
    correct = df['correct'].astype(bool).to_numpy()
    order = np.argsort(-confidence)
    for coverage in coverage_grid:
        retained_n = max(1, int(math.ceil(coverage * len(df))))
        retained = order[:retained_n]
        risk = 1.0 - correct[retained].mean()
        selective_rows.append({'architecture': architecture, 'seed': seed, 'coverage': coverage, 'retained_n': retained_n, 'selective_risk': risk})


selective = pd.DataFrame(selective_rows)


selective.to_csv(OUTPUT_DIR / '14_selective_risk_by_run.csv', index=False, encoding='utf-8-sig')


selective_summary = selective.groupby(['architecture', 'coverage']).agg(selective_risk_mean=('selective_risk', 'mean'), selective_risk_sd=('selective_risk', 'std')).reset_index()


selective_summary.to_csv(OUTPUT_DIR / '15_selective_risk_summary.csv', index=False, encoding='utf-8-sig')


fig, ax = plt.subplots(figsize=(8, 7))


for architecture in architecture_order:
    part = selective_summary[selective_summary['architecture'] == architecture]
    ax.plot(part['coverage'], part['selective_risk_mean'], marker='o', label=architecture)


ax.set_xlabel('Coverage')


ax.set_ylabel('Error rate among retained predictions')


ax.set_title('Selective risk on the internal E2-A test')


ax.legend(fontsize=8)


ax.grid(True, alpha=0.3)


fig.tight_layout()


save_figure(fig, 'Figure_selective_risk_all_architectures')


pairwise_rows = []
