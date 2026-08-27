for (architecture, seed), df in runs.items():
    prob_cols = probability_columns(df)
    probabilities = df[prob_cols].to_numpy(dtype=float)
    y_true = df['true_idx'].to_numpy(dtype=int)
    y_pred = df['pred_idx'].to_numpy(dtype=int)
    y_binary = label_binarize(y_true, classes=np.arange(len(EXPECTED_CLASSES)))
    accuracy = accuracy_score(y_true, y_pred)
    mean_confidence = probabilities.max(axis=1).mean()
    global_rows.append({'architecture': architecture, 'seed': seed, 'n': len(df), 'accuracy': accuracy, 'balanced_accuracy': balanced_accuracy_score(y_true, y_pred), 'macro_precision': precision_score(y_true, y_pred, average='macro', zero_division=0), 'macro_recall': recall_score(y_true, y_pred, average='macro', zero_division=0), 'macro_f1': f1_score(y_true, y_pred, average='macro'), 'weighted_f1': f1_score(y_true, y_pred, average='weighted'), 'mcc': matthews_corrcoef(y_true, y_pred), 'roc_auc_macro_ovr': roc_auc_score(y_binary, probabilities, average='macro', multi_class='ovr'), 'roc_auc_micro_ovr': roc_auc_score(y_binary, probabilities, average='micro', multi_class='ovr'), 'average_precision_macro': average_precision_score(y_binary, probabilities, average='macro'), 'average_precision_micro': average_precision_score(y_binary, probabilities, average='micro'), 'ece_15bins': expected_calibration_error(y_true, probabilities, n_bins=15), 'brier_multiclass': np.mean(np.sum((probabilities - y_binary) ** 2, axis=1)), 'log_loss': log_loss(y_true, probabilities, labels=np.arange(len(EXPECTED_CLASSES))), 'mean_confidence': mean_confidence, 'underconfidence_gap': accuracy - mean_confidence})
    precision, recall, f1_values, support = precision_recall_fscore_support(y_true, y_pred, labels=np.arange(len(EXPECTED_CLASSES)), zero_division=0)
    for class_idx, class_name in enumerate(EXPECTED_CLASSES):
        binary_true = (y_true == class_idx).astype(int)
        class_rows.append({'architecture': architecture, 'seed': seed, 'class_idx': class_idx, 'class_name': class_name, 'support': int(support[class_idx]), 'precision': precision[class_idx], 'recall': recall[class_idx], 'f1': f1_values[class_idx], 'roc_auc_ovr': roc_auc_score(binary_true, probabilities[:, class_idx]), 'average_precision': average_precision_score(binary_true, probabilities[:, class_idx])})
    reliability = reliability_table(y_true, probabilities, n_bins=15)
    reliability['architecture'] = architecture
    reliability['seed'] = seed
    reliability_rows.append(reliability)


global_metrics = pd.DataFrame(global_rows)


class_metrics = pd.DataFrame(class_rows)


reliability_all = pd.concat(reliability_rows, ignore_index=True)


global_metrics.to_csv(OUTPUT_DIR / '02_global_metrics_by_run.csv', index=False, encoding='utf-8-sig')


class_metrics.to_csv(OUTPUT_DIR / '03_class_metrics_by_run.csv', index=False, encoding='utf-8-sig')


reliability_all.to_csv(OUTPUT_DIR / '04_reliability_bins_by_run.csv', index=False, encoding='utf-8-sig')


global_summary = global_metrics.groupby('architecture').agg(runs=('seed', 'size'), accuracy_mean=('accuracy', 'mean'), accuracy_sd=('accuracy', 'std'), balanced_accuracy_mean=('balanced_accuracy', 'mean'), balanced_accuracy_sd=('balanced_accuracy', 'std'), macro_precision_mean=('macro_precision', 'mean'), macro_precision_sd=('macro_precision', 'std'), macro_recall_mean=('macro_recall', 'mean'), macro_recall_sd=('macro_recall', 'std'), macro_f1_mean=('macro_f1', 'mean'), macro_f1_sd=('macro_f1', 'std'), mcc_mean=('mcc', 'mean'), mcc_sd=('mcc', 'std'), roc_auc_macro_mean=('roc_auc_macro_ovr', 'mean'), roc_auc_macro_sd=('roc_auc_macro_ovr', 'std'), average_precision_macro_mean=('average_precision_macro', 'mean'), average_precision_macro_sd=('average_precision_macro', 'std'), ece_mean=('ece_15bins', 'mean'), ece_sd=('ece_15bins', 'std'), brier_mean=('brier_multiclass', 'mean'), brier_sd=('brier_multiclass', 'std'), log_loss_mean=('log_loss', 'mean'), log_loss_sd=('log_loss', 'std'), mean_confidence_mean=('mean_confidence', 'mean'), mean_confidence_sd=('mean_confidence', 'std'), underconfidence_gap_mean=('underconfidence_gap', 'mean'), underconfidence_gap_sd=('underconfidence_gap', 'std')).reset_index().sort_values('macro_f1_mean', ascending=False)


global_summary['macro_f1_mean_sd'] = global_summary.apply(lambda row: mean_sd_text(row['macro_f1_mean'], row['macro_f1_sd']), axis=1)


global_summary['accuracy_mean_sd'] = global_summary.apply(lambda row: mean_sd_text(row['accuracy_mean'], row['accuracy_sd']), axis=1)


global_summary['mcc_mean_sd'] = global_summary.apply(lambda row: mean_sd_text(row['mcc_mean'], row['mcc_sd']), axis=1)


global_summary.to_csv(OUTPUT_DIR / '05_global_summary_by_architecture.csv', index=False, encoding='utf-8-sig')


class_summary = class_metrics.groupby(['architecture', 'class_name']).agg(support=('support', 'first'), precision_mean=('precision', 'mean'), precision_sd=('precision', 'std'), recall_mean=('recall', 'mean'), recall_sd=('recall', 'std'), f1_mean=('f1', 'mean'), f1_sd=('f1', 'std'), roc_auc_mean=('roc_auc_ovr', 'mean'), roc_auc_sd=('roc_auc_ovr', 'std'), average_precision_mean=('average_precision', 'mean'), average_precision_sd=('average_precision', 'std')).reset_index()


class_summary.to_csv(OUTPUT_DIR / '06_class_summary_by_architecture.csv', index=False, encoding='utf-8-sig')


display(global_summary)


test_metrics = ['accuracy', 'balanced_accuracy', 'macro_f1', 'mcc', 'roc_auc_macro_ovr', 'average_precision_macro', 'ece_15bins', 'brier_multiclass', 'log_loss', 'mean_confidence', 'underconfidence_gap']


permutation_results = []


for metric in test_metrics:
    print('Testing:', metric)
    permutation_results.append(blocked_permutation_test(global_metrics, metric, n_permutations=N_PERMUTATIONS, random_seed=RANDOM_SEED))


permutation_results = pd.DataFrame(permutation_results)


permutation_results['holm_p'] = holm_adjust(permutation_results['permutation_p'].to_numpy())


permutation_results['significant_after_holm'] = permutation_results['holm_p'] < 0.05


permutation_results.to_csv(OUTPUT_DIR / '07_blocked_permutation_tests.csv', index=False, encoding='utf-8-sig')


display(permutation_results)


mcnemar_rows = []
