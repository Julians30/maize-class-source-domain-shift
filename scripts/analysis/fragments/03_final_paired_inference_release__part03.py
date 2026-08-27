for run_index in range(len(run_names)):
    run_prediction = predictions[run_index]
    for bootstrap_index in range(N_BOOTSTRAP):
        confusion = np.bincount(N_CLASSES * bootstrap_true[bootstrap_index] + run_prediction[bootstrap_indices[bootstrap_index]], minlength=N_CLASSES * N_CLASSES).reshape(N_CLASSES, N_CLASSES)
        metrics = metrics_from_confusion(confusion)
        run_macro_f1[run_index, bootstrap_index] = metrics['macro_f1']
        run_balanced_accuracy[run_index, bootstrap_index] = metrics['balanced_accuracy']
        run_class_f1[run_index, bootstrap_index] = metrics['class_f1']


architecture_macro_f1 = np.stack([run_macro_f1[architecture_index * len(SEEDS):(architecture_index + 1) * len(SEEDS)].mean(axis=0) for architecture_index in range(len(architecture_names))])


architecture_balanced_accuracy = np.stack([run_balanced_accuracy[architecture_index * len(SEEDS):(architecture_index + 1) * len(SEEDS)].mean(axis=0) for architecture_index in range(len(architecture_names))])


architecture_class_f1 = np.stack([run_class_f1[architecture_index * len(SEEDS):(architecture_index + 1) * len(SEEDS)].mean(axis=0) for architecture_index in range(len(architecture_names))])


print('Bootstrap completed:', N_BOOTSTRAP, 'replicates')


architecture_interval_rows = []


point_lookup = point_by_architecture.set_index('architecture')


for architecture_index, architecture in enumerate(architecture_names):
    lower, upper = percentile_interval(architecture_macro_f1[architecture_index])
    architecture_interval_rows.append({'architecture': architecture, 'macro_f1_mean': point_lookup.loc[architecture, 'macro_f1_mean'], 'bootstrap_ci95_lower': lower, 'bootstrap_ci95_upper': upper, 'macro_f1_sd_across_seeds': point_lookup.loc[architecture, 'macro_f1_sd']})


architecture_intervals = pd.DataFrame(architecture_interval_rows).sort_values('macro_f1_mean', ascending=False)


architecture_intervals.to_csv(OUTPUT_DIR / '04_macro_f1_architecture_bootstrap_intervals.csv', index=False, encoding='utf-8-sig')


display(architecture_intervals)


point_macro_f1 = point_lookup.loc[architecture_names, 'macro_f1_mean'].to_numpy()


pairwise_rows = []


for first_index, second_index in combinations(range(len(architecture_names)), 2):
    if point_macro_f1[first_index] >= point_macro_f1[second_index]:
        architecture_a_index = first_index
        architecture_b_index = second_index
    else:
        architecture_a_index = second_index
        architecture_b_index = first_index
    differences = architecture_macro_f1[architecture_a_index] - architecture_macro_f1[architecture_b_index]
    lower, upper = percentile_interval(differences)
    pairwise_rows.append({'architecture_a': architecture_names[architecture_a_index], 'architecture_b': architecture_names[architecture_b_index], 'difference_a_minus_b': point_macro_f1[architecture_a_index] - point_macro_f1[architecture_b_index], 'bootstrap_ci95_lower': lower, 'bootstrap_ci95_upper': upper, 'bootstrap_raw_p': bootstrap_two_sided_p(differences), 'ci_entirely_within_descriptive_0_01_band': bool(lower >= -0.01 and upper <= 0.01)})


pairwise = pd.DataFrame(pairwise_rows)


pairwise['holm_p'] = holm_adjust(pairwise['bootstrap_raw_p'].to_numpy())


pairwise['significant_after_holm'] = pairwise['holm_p'] < 0.05


pairwise = pairwise.sort_values('difference_a_minus_b', ascending=False)


pairwise.to_csv(OUTPUT_DIR / '05_pairwise_macro_f1_bootstrap_holm.csv', index=False, encoding='utf-8-sig')


display(pairwise)


class_interval_rows = []


for architecture_index, architecture in enumerate(architecture_names):
    for class_index, class_name in enumerate(EXPECTED_CLASSES):
        bootstrap_values = architecture_class_f1[architecture_index, :, class_index]
        lower, upper = percentile_interval(bootstrap_values)
        point_class_values = []
        for seed_index in range(len(SEEDS)):
            run_index = architecture_index * len(SEEDS) + seed_index
            confusion = np.bincount(N_CLASSES * y_true + predictions[run_index], minlength=N_CLASSES * N_CLASSES).reshape(N_CLASSES, N_CLASSES)
            point_class_values.append(metrics_from_confusion(confusion)['class_f1'][class_index])
        class_interval_rows.append({'architecture': architecture, 'class_name': class_name, 'support': int(np.sum(y_true == class_index)), 'class_f1_mean': float(np.mean(point_class_values)), 'class_f1_sd_across_seeds': float(np.std(point_class_values, ddof=1)), 'bootstrap_ci95_lower': lower, 'bootstrap_ci95_upper': upper})


class_intervals = pd.DataFrame(class_interval_rows)


class_intervals.to_csv(OUTPUT_DIR / '06_classwise_f1_bootstrap_intervals.csv', index=False, encoding='utf-8-sig')


display(class_intervals.sort_values(['class_f1_mean', 'architecture']).head(30))


seed_ensemble_predictions = []


seed_ensemble_probabilities = []


for seed_index, seed in enumerate(SEEDS):
    run_indices = [architecture_index * len(SEEDS) + seed_index for architecture_index in range(len(architecture_names))]
    mean_probability = probabilities[run_indices].mean(axis=0)
    seed_ensemble_probabilities.append(mean_probability)
    seed_ensemble_predictions.append(mean_probability.argmax(axis=1))


seed_ensemble_predictions = np.stack(seed_ensemble_predictions)


seed_ensemble_probabilities = np.stack(seed_ensemble_probabilities)


all_model_probability = probabilities.mean(axis=0)


all_model_prediction = all_model_probability.argmax(axis=1)


seed_ensemble_point_macro_f1 = np.array([f1_score(y_true, seed_ensemble_predictions[seed_index], average='macro') for seed_index in range(len(SEEDS))])


seed_ensemble_bootstrap = np.empty((len(SEEDS), N_BOOTSTRAP), dtype=np.float32)


for seed_index in range(len(SEEDS)):
    ensemble_prediction = seed_ensemble_predictions[seed_index]
    for bootstrap_index in range(N_BOOTSTRAP):
        confusion = np.bincount(N_CLASSES * bootstrap_true[bootstrap_index] + ensemble_prediction[bootstrap_indices[bootstrap_index]], minlength=N_CLASSES * N_CLASSES).reshape(N_CLASSES, N_CLASSES)
        seed_ensemble_bootstrap[seed_index, bootstrap_index] = metrics_from_confusion(confusion)['macro_f1']


six_architecture_ensemble_bootstrap = seed_ensemble_bootstrap.mean(axis=0)


six_architecture_ensemble_point = float(seed_ensemble_point_macro_f1.mean())


all_model_bootstrap = np.empty(N_BOOTSTRAP, dtype=np.float32)
