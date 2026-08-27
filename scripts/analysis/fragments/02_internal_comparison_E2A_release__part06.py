for seed in SEEDS:
    seed_runs = {architecture: runs[architecture, seed].set_index('sample_id') for architecture in ARCHITECTURES}
    for architecture_a, architecture_b in combinations(ARCHITECTURES, 2):
        a = seed_runs[architecture_a]
        b = seed_runs[architecture_b]
        y_true = a['true_idx'].to_numpy(dtype=int)
        pred_a = a['pred_idx'].to_numpy(dtype=int)
        pred_b = b['pred_idx'].to_numpy(dtype=int)
        pairwise_rows.append({'seed': seed, 'architecture_a': architecture_a, 'architecture_b': architecture_b, 'disagreement_rate': np.mean(pred_a != pred_b), 'prediction_kappa': cohen_kappa_score(pred_a, pred_b), 'double_fault_rate': np.mean((pred_a != y_true) & (pred_b != y_true)), 'pair_oracle_accuracy': np.mean((pred_a == y_true) | (pred_b == y_true))})


pairwise = pd.DataFrame(pairwise_rows)


pairwise.to_csv(OUTPUT_DIR / '16_pairwise_disagreement_by_seed.csv', index=False, encoding='utf-8-sig')


pairwise_summary = pairwise.groupby(['architecture_a', 'architecture_b']).agg(disagreement_mean=('disagreement_rate', 'mean'), disagreement_sd=('disagreement_rate', 'std'), kappa_mean=('prediction_kappa', 'mean'), double_fault_mean=('double_fault_rate', 'mean'), pair_oracle_accuracy_mean=('pair_oracle_accuracy', 'mean')).reset_index()


pairwise_summary.to_csv(OUTPUT_DIR / '17_pairwise_disagreement_summary.csv', index=False, encoding='utf-8-sig')


matrix = pd.DataFrame(np.eye(len(architecture_order)), index=architecture_order, columns=architecture_order)


for _, row in pairwise_summary.iterrows():
    matrix.loc[row['architecture_a'], row['architecture_b']] = row['disagreement_mean']
    matrix.loc[row['architecture_b'], row['architecture_a']] = row['disagreement_mean']


fig, ax = plt.subplots(figsize=(8, 7))


image = ax.imshow(matrix.to_numpy())


ax.set_xticks(np.arange(len(architecture_order)))


ax.set_xticklabels(architecture_order, rotation=45, ha='right')


ax.set_yticks(np.arange(len(architecture_order)))


ax.set_yticklabels(architecture_order)


ax.set_title('Mean pairwise prediction disagreement')


ax.set_xlabel('Architecture')


ax.set_ylabel('Architecture')


for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
        ax.text(j, i, f'{matrix.iloc[i, j]:.3f}', ha='center', va='center', fontsize=8)


fig.colorbar(image, ax=ax, label='Disagreement rate')


fig.tight_layout()


save_figure(fig, 'Figure_pairwise_disagreement')


prediction_wide = {}


correct_wide = {}


for (architecture, seed), df in runs.items():
    indexed = df.set_index('sample_id')
    run_name = f'{architecture}|seed_{seed}'
    prediction_wide[run_name] = indexed['pred_idx']
    correct_wide[run_name] = indexed['correct'].astype(bool)


prediction_wide = pd.DataFrame(prediction_wide)


correct_wide = pd.DataFrame(correct_wide)


correct_count = correct_wide.sum(axis=1)


consensus_distribution = correct_count.value_counts().sort_index().rename_axis('number_of_correct_runs').reset_index(name='images')


consensus_distribution['proportion'] = consensus_distribution['images'] / EXPECTED_N


consensus_distribution.to_csv(OUTPUT_DIR / '18_consensus_correctness_distribution.csv', index=False, encoding='utf-8-sig')


reference = next(iter(runs.values())).set_index('sample_id')


hard_case_rows = []


for sample_id in correct_count[correct_count < 18].index:
    predictions = prediction_wide.loc[sample_id].astype(int)
    prediction_names = predictions.map(lambda value: EXPECTED_CLASSES[int(value)])
    mode = prediction_names.mode().iloc[0]
    hard_case_rows.append({'sample_id': sample_id, 'sha256': reference.loc[sample_id, 'sha256'], 'global_group_id': reference.loc[sample_id, 'global_group_id'], 'true_class': reference.loc[sample_id, 'true_class'], 'source_operational': reference.loc[sample_id, 'source_operational'], 'filename': reference.loc[sample_id, 'filename'], 'correct_runs': int(correct_count.loc[sample_id]), 'incorrect_runs': int(18 - correct_count.loc[sample_id]), 'modal_prediction': mode, 'modal_prediction_count': int((prediction_names == mode).sum())})


hard_cases = pd.DataFrame(hard_case_rows).sort_values(['correct_runs', 'true_class', 'sample_id'])


hard_cases.to_csv(OUTPUT_DIR / '19_shared_hard_cases.csv', index=False, encoding='utf-8-sig')


fig, ax = plt.subplots(figsize=(10, 6))


ax.bar(consensus_distribution['number_of_correct_runs'].astype(str), consensus_distribution['images'])


ax.set_xlabel('Number of correct predictions among 18 runs')


ax.set_ylabel('Images')


ax.set_title('Agreement in correctness across all architectures and seeds')


ax.grid(True, axis='y', alpha=0.3)


fig.tight_layout()


save_figure(fig, 'Figure_correctness_consensus_18_runs')


print('Images correct in all 18 runs:', int((correct_count == 18).sum()))


print('Images wrong in all 18 runs:', int((correct_count == 0).sum()))


display(consensus_distribution)


display(hard_cases.head(30))


ensemble_rows = []


for seed in SEEDS:
    seed_dfs = [runs[architecture, seed] for architecture in ARCHITECTURES]
    probabilities = np.mean([df[probability_columns(df)].to_numpy(dtype=float) for df in seed_dfs], axis=0)
    y_true = seed_dfs[0]['true_idx'].to_numpy(dtype=int)
    y_pred = probabilities.argmax(axis=1)
    y_binary = label_binarize(y_true, classes=np.arange(len(EXPECTED_CLASSES)))
    ensemble_rows.append({'ensemble': 'Six-architecture soft vote', 'seed': seed, 'models': 6, 'accuracy': accuracy_score(y_true, y_pred), 'balanced_accuracy': balanced_accuracy_score(y_true, y_pred), 'macro_f1': f1_score(y_true, y_pred, average='macro'), 'mcc': matthews_corrcoef(y_true, y_pred), 'roc_auc_macro_ovr': roc_auc_score(y_binary, probabilities, average='macro', multi_class='ovr'), 'average_precision_macro': average_precision_score(y_binary, probabilities, average='macro'), 'ece_15bins': expected_calibration_error(y_true, probabilities, n_bins=15), 'log_loss': log_loss(y_true, probabilities)})


all_dfs = list(runs.values())


all_probabilities = np.mean([df[probability_columns(df)].to_numpy(dtype=float) for df in all_dfs], axis=0)


y_true = all_dfs[0]['true_idx'].to_numpy(dtype=int)


y_pred = all_probabilities.argmax(axis=1)


y_binary = label_binarize(y_true, classes=np.arange(len(EXPECTED_CLASSES)))
