for seed in SEEDS:
    seed_runs = {architecture: runs[architecture, seed].set_index('sample_id') for architecture in ARCHITECTURES}
    for architecture_a, architecture_b in combinations(ARCHITECTURES, 2):
        a = seed_runs[architecture_a]
        b = seed_runs[architecture_b]
        correct_a = a['pred_idx'].to_numpy() == a['true_idx'].to_numpy()
        correct_b = b['pred_idx'].to_numpy() == b['true_idx'].to_numpy()
        a_only = int(np.sum(correct_a & ~correct_b))
        b_only = int(np.sum(~correct_a & correct_b))
        discordant = a_only + b_only
        if discordant == 0:
            p_value = 1.0
        else:
            p_value = binomtest(min(a_only, b_only), n=discordant, p=0.5, alternative='two-sided').pvalue
        mcnemar_rows.append({'seed': seed, 'architecture_a': architecture_a, 'architecture_b': architecture_b, 'a_correct_b_wrong': a_only, 'a_wrong_b_correct': b_only, 'discordant': discordant, 'raw_p': p_value, 'direction': architecture_a if a_only > b_only else architecture_b if b_only > a_only else 'tie'})


mcnemar = pd.DataFrame(mcnemar_rows)


adjusted_parts = []


for seed, part in mcnemar.groupby('seed', sort=True):
    part = part.copy()
    part['holm_p'] = holm_adjust(part['raw_p'].to_numpy())
    part['significant_after_holm'] = part['holm_p'] < 0.05
    adjusted_parts.append(part)


mcnemar = pd.concat(adjusted_parts, ignore_index=True)


mcnemar.to_csv(OUTPUT_DIR / '08_mcnemar_pairwise_by_seed.csv', index=False, encoding='utf-8-sig')


display(mcnemar.sort_values(['seed', 'holm_p']).head(30))


architecture_order = global_summary['architecture'].tolist()


x = np.arange(len(architecture_order))


fig, ax = plt.subplots(figsize=(10, 6))


for index, architecture in enumerate(architecture_order):
    values = global_metrics.loc[global_metrics['architecture'] == architecture, 'macro_f1'].sort_index().to_numpy()
    ax.scatter(np.repeat(index, len(values)), values, s=50)


means = global_metrics.groupby('architecture')['macro_f1'].mean().reindex(architecture_order)


standard_deviations = global_metrics.groupby('architecture')['macro_f1'].std().reindex(architecture_order)


ax.errorbar(x, means, yerr=standard_deviations, fmt='o', capsize=5, markersize=8)


ax.set_xticks(x)


ax.set_xticklabels(architecture_order, rotation=35, ha='right')


ax.set_ylabel('Internal test macro-F1')


ax.set_xlabel('Architecture')


ax.set_title('Internal E2-A performance across three seeds')


ax.grid(True, axis='y', alpha=0.3)


fig.tight_layout()


save_figure(fig, 'Figure_1_internal_macro_f1_by_architecture')


for metric, label in [('f1_mean', 'Mean class-wise F1'), ('recall_mean', 'Mean class-wise recall'), ('average_precision_mean', 'Mean class-wise average precision')]:
    matrix = class_summary.pivot(index='architecture', columns='class_name', values=metric).reindex(index=architecture_order, columns=EXPECTED_CLASSES)
    fig, ax = plt.subplots(figsize=(13, 6))
    image = ax.imshow(matrix.to_numpy(), aspect='auto')
    ax.set_xticks(np.arange(len(EXPECTED_CLASSES)))
    ax.set_xticklabels(EXPECTED_CLASSES, rotation=45, ha='right')
    ax.set_yticks(np.arange(len(architecture_order)))
    ax.set_yticklabels(architecture_order)
    ax.set_xlabel('Operational class')
    ax.set_ylabel('Architecture')
    ax.set_title(label)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f'{matrix.iloc[i, j]:.3f}', ha='center', va='center', fontsize=8)
    fig.colorbar(image, ax=ax, label=label)
    fig.tight_layout()
    save_figure(fig, f'Figure_class_heatmap_{metric}')


confusion_rows = []


for architecture in ARCHITECTURES:
    matrices = []
    for seed in SEEDS:
        df = runs[architecture, seed]
        cm = confusion_matrix(df['true_idx'], df['pred_idx'], labels=np.arange(len(EXPECTED_CLASSES)), normalize='true')
        matrices.append(cm)
    mean_matrix = np.mean(matrices, axis=0)
    for true_idx, true_class in enumerate(EXPECTED_CLASSES):
        for pred_idx, pred_class in enumerate(EXPECTED_CLASSES):
            confusion_rows.append({'architecture': architecture, 'true_class': true_class, 'predicted_class': pred_class, 'mean_row_normalized_proportion': mean_matrix[true_idx, pred_idx]})
    fig, ax = plt.subplots(figsize=(10, 8))
    image = ax.imshow(mean_matrix, vmin=0.0, vmax=1.0)
    ax.set_xticks(np.arange(len(EXPECTED_CLASSES)))
    ax.set_xticklabels(EXPECTED_CLASSES, rotation=45, ha='right')
    ax.set_yticks(np.arange(len(EXPECTED_CLASSES)))
    ax.set_yticklabels(EXPECTED_CLASSES)
    ax.set_xlabel('Predicted class')
    ax.set_ylabel('True class')
    ax.set_title(f'{architecture}: mean normalized confusion matrix')
    for i in range(mean_matrix.shape[0]):
        for j in range(mean_matrix.shape[1]):
            ax.text(j, i, f'{mean_matrix[i, j]:.2f}', ha='center', va='center', fontsize=7)
    fig.colorbar(image, ax=ax, label='Row-normalized proportion')
    fig.tight_layout()
    safe_name = architecture.replace('/', '_').replace(' ', '_')
    save_figure(fig, f'Confusion_matrix_{safe_name}')


confusion_summary = pd.DataFrame(confusion_rows)


confusion_summary.to_csv(OUTPUT_DIR / '09_mean_normalized_confusion_matrices.csv', index=False, encoding='utf-8-sig')


error_destinations = confusion_summary[confusion_summary['true_class']].sort_values(['architecture', 'true_class', 'mean_row_normalized_proportion'], ascending=[True, True, False]).groupby(['architecture', 'true_class']).head(3)


error_destinations.to_csv(OUTPUT_DIR / '10_top_error_destinations_by_architecture.csv', index=False, encoding='utf-8-sig')


common_fpr = np.linspace(0.0, 1.0, 1001)


roc_rows = []


fig, ax = plt.subplots(figsize=(8, 7))
