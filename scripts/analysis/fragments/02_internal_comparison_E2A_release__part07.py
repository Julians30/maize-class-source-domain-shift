ensemble_rows.append({'ensemble': 'Eighteen-model soft vote', 'seed': 'all', 'models': 18, 'accuracy': accuracy_score(y_true, y_pred), 'balanced_accuracy': balanced_accuracy_score(y_true, y_pred), 'macro_f1': f1_score(y_true, y_pred, average='macro'), 'mcc': matthews_corrcoef(y_true, y_pred), 'roc_auc_macro_ovr': roc_auc_score(y_binary, all_probabilities, average='macro', multi_class='ovr'), 'average_precision_macro': average_precision_score(y_binary, all_probabilities, average='macro'), 'ece_15bins': expected_calibration_error(y_true, all_probabilities, n_bins=15), 'log_loss': log_loss(y_true, all_probabilities)})


ensemble_metrics = pd.DataFrame(ensemble_rows)


ensemble_metrics.to_csv(OUTPUT_DIR / '20_soft_voting_ensemble_metrics.csv', index=False, encoding='utf-8-sig')


display(ensemble_metrics)


registry = pd.read_csv(REGISTRY_PATH)


registry = registry[registry['direction'] == 'E2_A'].copy()


complexity = registry.groupby('architecture').agg(family=('family', 'first'), parameters=('num_parameters', 'first'), gpu_name=('gpu_name', 'first'), selected_epoch_mean=('best_epoch', 'mean'), selected_epoch_sd=('best_epoch', 'std')).reset_index()


time_audit = pd.read_csv(TIME_AUDIT_PATH, encoding='utf-8-sig')


time_audit = time_audit[time_audit['experiment'].astype(str) == 'E2_A'].copy()


time_name_map = {'efficientnet_b0': 'EfficientNet-B0', 'mobilenetv3_large': 'MobileNetV3-Large', 'mobilevit_s': 'MobileViT-S', 'resnet50': 'ResNet50', 'swin_tiny_patch4_window7_224': 'Swin-Tiny', 'vit_base_patch16_224': 'ViT-Base/16'}


time_audit['architecture'] = time_audit['architecture'].map(time_name_map)


complexity = complexity.merge(time_audit[['architecture', 'hardware_hint', 'mean_total_minutes', 'std_total_minutes', 'min_total_minutes', 'max_total_minutes', 'mean_epochs_trained']], on='architecture', how='left', validate='one_to_one')


complexity = complexity.merge(global_summary[['architecture', 'macro_f1_mean', 'macro_f1_sd']], on='architecture', how='left', validate='one_to_one')


complexity['parameters_millions'] = complexity['parameters'] / 1000000


complexity['mean_total_hours'] = complexity['mean_total_minutes'] / 60.0


complexity.to_csv(OUTPUT_DIR / '21_complexity_and_l4_training_time.csv', index=False, encoding='utf-8-sig')


fig, ax = plt.subplots(figsize=(8, 7))


ax.scatter(complexity['parameters_millions'], complexity['macro_f1_mean'], s=80)


for _, row in complexity.iterrows():
    ax.annotate(row['architecture'], (row['parameters_millions'], row['macro_f1_mean']), xytext=(5, 5), textcoords='offset points', fontsize=8)


ax.set_xlabel('Trainable parameters (millions)')


ax.set_ylabel('Mean internal macro-F1')


ax.set_title('Model size and internal performance')


ax.grid(True, alpha=0.3)


fig.tight_layout()


save_figure(fig, 'Figure_parameters_vs_macro_f1')


fig, ax = plt.subplots(figsize=(8, 7))


ax.scatter(complexity['mean_total_minutes'], complexity['macro_f1_mean'], s=80)


for _, row in complexity.iterrows():
    ax.annotate(row['architecture'], (row['mean_total_minutes'], row['macro_f1_mean']), xytext=(5, 5), textcoords='offset points', fontsize=8)


ax.set_xlabel('Mean E2-A training time on NVIDIA L4 (minutes)')


ax.set_ylabel('Mean internal macro-F1')


ax.set_title('Observed training time and internal performance')


ax.grid(True, alpha=0.3)


fig.tight_layout()


save_figure(fig, 'Figure_l4_training_time_vs_macro_f1')


display(complexity.sort_values('macro_f1_mean', ascending=False))


best_f1 = global_summary.iloc[0]


best_auc = global_summary.loc[global_summary['roc_auc_macro_mean'].idxmax()]


best_ap = global_summary.loc[global_summary['average_precision_macro_mean'].idxmax()]


most_stable = global_summary.loc[global_summary['macro_f1_sd'].idxmin()]


least_stable = global_summary.loc[global_summary['macro_f1_sd'].idxmax()]


class_overall = class_metrics.groupby('class_name').agg(support=('support', 'first'), recall_mean=('recall', 'mean'), f1_mean=('f1', 'mean'), roc_auc_mean=('roc_auc_ovr', 'mean'), average_precision_mean=('average_precision', 'mean')).reset_index().sort_values('f1_mean')


class_overall.to_csv(OUTPUT_DIR / '22_overall_class_difficulty.csv', index=False, encoding='utf-8-sig')


all_correct = int((pd.DataFrame({key: df.set_index('sample_id')['correct'].astype(bool) for key, df in runs.items()}).sum(axis=1) == 18).sum())


all_wrong = int((pd.DataFrame({key: df.set_index('sample_id')['correct'].astype(bool) for key, df in runs.items()}).sum(axis=1) == 0).sum())


findings = {'validated_runs': len(runs), 'internal_test_images': EXPECTED_N, 'best_mean_macro_f1_architecture': best_f1['architecture'], 'best_mean_macro_f1': float(best_f1['macro_f1_mean']), 'best_macro_auc_architecture': best_auc['architecture'], 'best_mean_macro_auc': float(best_auc['roc_auc_macro_mean']), 'best_macro_average_precision_architecture': best_ap['architecture'], 'best_mean_macro_average_precision': float(best_ap['average_precision_macro_mean']), 'most_stable_macro_f1_architecture': most_stable['architecture'], 'smallest_macro_f1_sd': float(most_stable['macro_f1_sd']), 'least_stable_macro_f1_architecture': least_stable['architecture'], 'largest_macro_f1_sd': float(least_stable['macro_f1_sd']), 'hardest_class_by_mean_f1': class_overall.iloc[0]['class_name'], 'hardest_class_mean_f1': float(class_overall.iloc[0]['f1_mean']), 'images_correct_in_all_18_runs': all_correct, 'images_wrong_in_all_18_runs': all_wrong, 'eighteen_model_ensemble_macro_f1': float(ensemble_metrics.loc[ensemble_metrics['ensemble'] == 'Eighteen-model soft vote', 'macro_f1'].iloc[0])}


findings_path = OUTPUT_DIR / 'MANUSCRIPT_preliminary_findings.json'


findings_path.write_text(json.dumps(findings, indent=2, ensure_ascii=False), encoding='utf-8')


print(json.dumps(findings, indent=2, ensure_ascii=False))


display(class_overall)


zip_path = OUTPUT_DIR.parent / 'internal_comparison_reproduction_outputs.zip'


if zip_path.exists():
    zip_path.unlink()


with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in OUTPUT_DIR.rglob('*'):
        if path.is_file():
            archive.write(path, arcname=path.relative_to(OUTPUT_DIR))


print('Completed successfully.')


print('Output folder:', OUTPUT_DIR)


print('Reproduction ZIP:', zip_path)
