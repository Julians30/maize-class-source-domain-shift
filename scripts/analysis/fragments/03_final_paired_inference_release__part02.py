for architecture, folder_name in ARCHITECTURES.items():
    for seed in SEEDS:
        path = E2_ROOT / f'{folder_name}_seed{seed}_internal_test_predictions_release.csv'
        if not path.exists():
            raise FileNotFoundError(path)
        dataframe = pd.read_csv(path)
        dataframe = dataframe.sort_values('sample_id').reset_index(drop=True)
        probability_cols = probability_columns(dataframe)
        probabilities = dataframe[probability_cols].to_numpy(dtype=float)
        required_columns = {'sha256', 'global_group_id', 'sample_id', 'true_idx', 'true_class', 'pred_idx', 'pred_class', 'confidence', 'correct'}
        missing = required_columns - set(dataframe.columns)
        if missing:
            raise ValueError(f'{path} is missing: {sorted(missing)}')
        keys = dataframe[['sha256', 'global_group_id', 'sample_id', 'true_idx', 'true_class']].copy()
        if reference_keys is None:
            reference_keys = keys
        elif not reference_keys.equals(keys):
            raise ValueError(f'Image ordering or labels differ for {architecture}, seed {seed}')
        predicted_from_probabilities = probabilities.argmax(axis=1)
        confidence_from_probabilities = probabilities.max(axis=1)
        stored_correct = dataframe['correct'].astype(bool).to_numpy()
        recomputed_correct = dataframe['pred_idx'].to_numpy() == dataframe['true_idx'].to_numpy()
        validation_rows.append({'architecture': architecture, 'seed': seed, 'n': len(dataframe), 'unique_sample_id': dataframe['sample_id'].nunique(), 'unique_sha256': dataframe['sha256'].nunique(), 'unique_groups': dataframe['global_group_id'].nunique(), 'probability_columns': len(probability_cols), 'probability_sum_max_abs_error': float(np.max(np.abs(probabilities.sum(axis=1) - 1.0))), 'pred_idx_argmax_mismatches': int(np.sum(dataframe['pred_idx'].to_numpy() != predicted_from_probabilities)), 'confidence_maxprob_max_abs_error': float(np.max(np.abs(dataframe['confidence'].to_numpy() - confidence_from_probabilities))), 'correct_flag_mismatches': int(np.sum(stored_correct != recomputed_correct)), 'missing_values': int(dataframe.isna().sum().sum())})
        runs[architecture, seed] = dataframe


validation = pd.DataFrame(validation_rows)


validation.to_csv(OUTPUT_DIR / '01_strict_prediction_validation.csv', index=False, encoding='utf-8-sig')


if len(runs) != 18:
    raise RuntimeError(f'Expected 18 runs, found {len(runs)}')


if not (validation['n'] == EXPECTED_N).all():
    raise RuntimeError('Unexpected internal test size')


if not (validation['unique_sample_id'] == EXPECTED_N).all():
    raise RuntimeError('Duplicate or missing sample identifiers')


if not (validation['unique_groups'] == EXPECTED_N).all():
    raise RuntimeError('Duplicate or missing test groups')


if validation['missing_values'].sum() != 0:
    raise RuntimeError('Missing values detected')


if validation['pred_idx_argmax_mismatches'].sum() != 0:
    raise RuntimeError('Stored predictions do not match probability argmax')


if validation['correct_flag_mismatches'].sum() != 0:
    raise RuntimeError('Stored correctness flags are inconsistent')


if validation['confidence_maxprob_max_abs_error'].max() > 1e-10:
    raise RuntimeError('Stored confidence does not match maximum probability')


if validation['probability_sum_max_abs_error'].max() > 1e-06:
    raise RuntimeError('Probability vectors do not sum to one')


print('Strict validation passed for 18/18 runs.')


display(validation)


architecture_names = list(ARCHITECTURES.keys())


run_names = [(architecture, seed) for architecture in architecture_names for seed in SEEDS]


reference_dataframe = runs[run_names[0]]


y_true = reference_dataframe['true_idx'].to_numpy(dtype=np.int16)


predictions = np.stack([runs[run_name]['pred_idx'].to_numpy(dtype=np.int16) for run_name in run_names])


confidences = np.stack([runs[run_name]['confidence'].to_numpy(dtype=np.float32) for run_name in run_names])


probabilities = np.stack([runs[run_name][probability_columns(runs[run_name])].to_numpy(dtype=np.float32) for run_name in run_names])


point_rows = []


for run_index, (architecture, seed) in enumerate(run_names):
    confusion = np.bincount(N_CLASSES * y_true + predictions[run_index], minlength=N_CLASSES * N_CLASSES).reshape(N_CLASSES, N_CLASSES)
    metrics = metrics_from_confusion(confusion)
    correct = predictions[run_index] == y_true
    aurc, _, _ = exact_aurc(correct, confidences[run_index])
    point_rows.append({'architecture': architecture, 'seed': seed, 'accuracy': accuracy_score(y_true, predictions[run_index]), 'balanced_accuracy': metrics['balanced_accuracy'], 'macro_f1': metrics['macro_f1'], 'mcc': matthews_corrcoef(y_true, predictions[run_index]), 'mean_confidence': float(confidences[run_index].mean()), 'underconfidence_gap': float(accuracy_score(y_true, predictions[run_index]) - confidences[run_index].mean()), 'aurc': aurc})


point_by_run = pd.DataFrame(point_rows)


point_by_run.to_csv(OUTPUT_DIR / '02_point_metrics_by_run.csv', index=False, encoding='utf-8-sig')


point_by_architecture = point_by_run.groupby('architecture').agg(accuracy_mean=('accuracy', 'mean'), accuracy_sd=('accuracy', 'std'), balanced_accuracy_mean=('balanced_accuracy', 'mean'), balanced_accuracy_sd=('balanced_accuracy', 'std'), macro_f1_mean=('macro_f1', 'mean'), macro_f1_sd=('macro_f1', 'std'), mcc_mean=('mcc', 'mean'), mcc_sd=('mcc', 'std'), confidence_mean=('mean_confidence', 'mean'), confidence_sd=('mean_confidence', 'std'), underconfidence_gap_mean=('underconfidence_gap', 'mean'), underconfidence_gap_sd=('underconfidence_gap', 'std'), aurc_mean=('aurc', 'mean'), aurc_sd=('aurc', 'std')).reset_index()


point_by_architecture.to_csv(OUTPUT_DIR / '03_point_summary_by_architecture.csv', index=False, encoding='utf-8-sig')


display(point_by_architecture.sort_values('macro_f1_mean', ascending=False))


random_generator = np.random.default_rng(RANDOM_SEED)


class_indices = [np.where(y_true == class_index)[0] for class_index in range(N_CLASSES)]


bootstrap_indices = np.concatenate([random_generator.choice(indices, size=(N_BOOTSTRAP, len(indices)), replace=True) for indices in class_indices], axis=1).astype(np.int32)


bootstrap_true = y_true[bootstrap_indices]


run_macro_f1 = np.empty((len(run_names), N_BOOTSTRAP), dtype=np.float32)


run_balanced_accuracy = np.empty_like(run_macro_f1)


run_class_f1 = np.empty((len(run_names), N_BOOTSTRAP, N_CLASSES), dtype=np.float32)
