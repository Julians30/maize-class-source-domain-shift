def blocked_permutation_test(data, value_column, n_permutations=50000, random_seed=0):
    result = blocked_architecture_f(data, value_column)
    ordered = result['data']
    reduced = result['reduced']
    full = result['full']
    df_arch = result['df_architecture']
    df_error = result['df_error']
    matrix = ordered.pivot(index='seed', columns='architecture', values=value_column).loc[result['seeds'], result['architectures']].to_numpy(dtype=float)

    def f_from_vector(y):
        beta_reduced = np.linalg.lstsq(reduced, y, rcond=None)[0]
        residual_reduced = y - reduced @ beta_reduced
        rss_reduced = float(residual_reduced @ residual_reduced)
        beta_full = np.linalg.lstsq(full, y, rcond=None)[0]
        residual_full = y - full @ beta_full
        rss_full = float(residual_full @ residual_full)
        return (rss_reduced - rss_full) / df_arch / (rss_full / df_error)
    observed = f_from_vector(matrix.reshape(-1))
    rng = np.random.default_rng(random_seed)
    exceedances = 0
    for _ in range(n_permutations):
        permuted = np.vstack([rng.permutation(row) for row in matrix])
        if f_from_vector(permuted.reshape(-1)) >= observed:
            exceedances += 1
    p_value = (exceedances + 1) / (n_permutations + 1)
    return {'metric': value_column, 'F': float(observed), 'df1': int(df_arch), 'df2': int(df_error), 'permutation_p': float(p_value), 'n_permutations': int(n_permutations)}


def mean_sd_text(mean_value, sd_value, digits=4):
    return f'{mean_value:.{digits}f} ± {sd_value:.{digits}f}'


def save_figure(fig, stem):
    png = OUTPUT_DIR / f'{stem}.png'
    pdf = OUTPUT_DIR / f'{stem}.pdf'
    fig.savefig(png, dpi=300, bbox_inches='tight')
    fig.savefig(pdf, bbox_inches='tight')
    plt.close(fig)
    return (png, pdf)


runs = {}


validation_rows = []


reference_keys = None


for architecture, model_key in ARCHITECTURES.items():
    for seed in SEEDS:
        path = E2_ROOT / f'{model_key}_seed{seed}_internal_test_predictions_release.csv'
        if not path.exists():
            raise FileNotFoundError(f'Missing required file: {path}')
        df = pd.read_csv(path)
        prob_cols = probability_columns(df)
        df = df.sort_values('sample_id').reset_index(drop=True)
        required = {'sha256', 'global_group_id', 'sample_id', 'true_idx', 'true_class', 'pred_idx', 'pred_class', 'confidence', 'correct'}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f'{path} is missing columns: {sorted(missing)}')
        keys = df[['sha256', 'global_group_id', 'sample_id', 'true_idx', 'true_class']].copy()
        if reference_keys is None:
            reference_keys = keys
        elif not reference_keys.equals(keys):
            raise ValueError(f'Sample order or labels differ for {architecture}, seed {seed}')
        probabilities = df[prob_cols].to_numpy(dtype=float)
        probability_sums = probabilities.sum(axis=1)
        correctness = df['true_idx'].to_numpy() == df['pred_idx'].to_numpy()
        validation_rows.append({'architecture': architecture, 'seed': seed, 'n': len(df), 'unique_sample_id': df['sample_id'].nunique(), 'unique_sha256': df['sha256'].nunique(), 'unique_groups': df['global_group_id'].nunique(), 'probability_columns': len(prob_cols), 'probability_sum_min': probability_sums.min(), 'probability_sum_max': probability_sums.max(), 'missing_values': int(df.isna().sum().sum()), 'correct_flag_consistent': bool(np.array_equal(correctness, df['correct'].astype(bool).to_numpy()))})
        runs[architecture, seed] = df


validation = pd.DataFrame(validation_rows)


validation.to_csv(OUTPUT_DIR / '01_data_integrity_validation.csv', index=False, encoding='utf-8-sig')


if len(runs) != 18:
    raise RuntimeError(f'Expected 18 runs, found {len(runs)}')


if not (validation['n'] == EXPECTED_N).all():
    raise RuntimeError('At least one run does not contain 1,719 observations')


if not (validation['probability_columns'] == 9).all():
    raise RuntimeError('At least one run does not contain nine probability columns')


if not np.allclose(validation['probability_sum_min'], 1.0, atol=1e-06):
    raise RuntimeError('Probability sums are invalid')


if not np.allclose(validation['probability_sum_max'], 1.0, atol=1e-06):
    raise RuntimeError('Probability sums are invalid')


if validation['missing_values'].sum() != 0:
    raise RuntimeError('Missing values were detected')


if not validation['correct_flag_consistent'].all():
    raise RuntimeError('The stored correct flag is inconsistent')


print('Validated 18/18 runs.')


print('All runs contain the same 1,719 unique images and groups.')


display(validation)


global_rows = []


class_rows = []


reliability_rows = []
