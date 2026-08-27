#!/usr/bin/env python3


"""Release-safe analytical source reconstructed from the frozen project notebook.

This file preserves the notebook code sequence while removing execution outputs,
Colab-only metadata, and private absolute paths. Runtime paths are parameterized.
"""


'Internal E2-A architecture comparison\n\nRelease-safe Python export derived from the executed manuscript-facing notebook.\nNotebook outputs and Colab identity metadata are intentionally excluded.\n'


try:
    from IPython.display import display
except ImportError:

    def display(obj):
        print(obj)


from pathlib import Path


import os


from itertools import combinations


import json


import math


import shutil


import zipfile


import numpy as np


import pandas as pd


import matplotlib.pyplot as plt


from scipy.stats import binomtest


from sklearn.metrics import accuracy_score, balanced_accuracy_score, precision_score, recall_score, f1_score, precision_recall_fscore_support, matthews_corrcoef, log_loss, roc_auc_score, average_precision_score, roc_curve, precision_recall_curve, confusion_matrix, cohen_kappa_score


from sklearn.preprocessing import label_binarize


RANDOM_SEED = 20260803


N_PERMUTATIONS = 50000


REPO_ROOT = Path(os.environ.get('MAIZE_REPO_ROOT', '.')).resolve()


E2_ROOT = Path(os.environ.get('MAIZE_E2_ROOT', REPO_ROOT / 'predictions' / 'internal_E2A')).resolve()


REGISTRY_PATH = Path(os.environ.get('MAIZE_RUN_REGISTRY', REPO_ROOT / 'manifests' / 'e2_run_registry_v4.csv')).resolve()


TIME_AUDIT_PATH = Path(os.environ.get('MAIZE_TIME_AUDIT', REPO_ROOT / 'results' / 'computational_cost' / 'training_time_summary_by_architecture.csv')).resolve()


OUTPUT_DIR = Path(os.environ.get('MAIZE_OUTPUT_DIR', REPO_ROOT / 'results' / 'reproduction' / 'internal_comparison')).resolve()


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


ARCHITECTURES = {'EfficientNet-B0': 'efficientnet_b0', 'MobileNetV3-Large': 'mobilenetv3_large', 'MobileViT-S': 'mobilevit_s', 'ResNet50': 'resnet50', 'Swin-Tiny': 'swin_tiny_patch4_window7_224', 'ViT-Base/16': 'vit_base_patch16_224'}


SEEDS = [17, 42, 73]


EXPECTED_N = 1719


EXPECTED_CLASSES = ['fall_armyworm', 'grasshopper', 'healthy', 'leaf_beetle', 'leaf_blight', 'leaf_spot', 'lethal_necrosis', 'rust', 'streak_virus']


print('E2 prediction root:', E2_ROOT)


print('OUTPUT_DIR:', OUTPUT_DIR)


def probability_columns(df):
    cols = [c for c in df.columns if c.startswith('prob_')]
    return sorted(cols, key=lambda c: int(c.split('_')[1]))


def expected_calibration_error(y_true, probabilities, n_bins=15):
    confidence = probabilities.max(axis=1)
    prediction = probabilities.argmax(axis=1)
    correct = prediction == y_true
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        if i == n_bins - 1:
            mask = (confidence >= edges[i]) & (confidence <= edges[i + 1])
        else:
            mask = (confidence >= edges[i]) & (confidence < edges[i + 1])
        if mask.any():
            ece += mask.mean() * abs(correct[mask].mean() - confidence[mask].mean())
    return float(ece)


def reliability_table(y_true, probabilities, n_bins=15):
    confidence = probabilities.max(axis=1)
    prediction = probabilities.argmax(axis=1)
    correct = prediction == y_true
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    rows = []
    for i in range(n_bins):
        if i == n_bins - 1:
            mask = (confidence >= edges[i]) & (confidence <= edges[i + 1])
        else:
            mask = (confidence >= edges[i]) & (confidence < edges[i + 1])
        rows.append({'bin': i + 1, 'lower': edges[i], 'upper': edges[i + 1], 'n': int(mask.sum()), 'mean_confidence': float(confidence[mask].mean()) if mask.any() else np.nan, 'accuracy': float(correct[mask].mean()) if mask.any() else np.nan})
    return pd.DataFrame(rows)


def holm_adjust(p_values):
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    adjusted = np.empty_like(p)
    running = 0.0
    m = len(p)
    for rank, idx in enumerate(order):
        value = (m - rank) * p[idx]
        running = max(running, value)
        adjusted[idx] = min(running, 1.0)
    return adjusted


def blocked_architecture_f(data, value_column):
    data = data[['architecture', 'seed', value_column]].copy()
    architectures = sorted(data['architecture'].unique())
    seeds = sorted(data['seed'].unique())
    data['architecture'] = pd.Categorical(data['architecture'], categories=architectures, ordered=True)
    data['seed'] = pd.Categorical(data['seed'], categories=seeds, ordered=True)
    data['_arch'] = data['architecture'].cat.codes
    data['_seed'] = data['seed'].cat.codes
    data = data.sort_values(['_seed', '_arch']).reset_index(drop=True)
    n = len(data)
    seed_dummies = pd.get_dummies(data['seed'], drop_first=True).to_numpy(dtype=float)
    arch_dummies = pd.get_dummies(data['architecture'], drop_first=True).to_numpy(dtype=float)
    reduced = np.column_stack([np.ones(n), seed_dummies])
    full = np.column_stack([reduced, arch_dummies])
    y = data[value_column].to_numpy(dtype=float)

    def residual_sum_squares(design, response):
        coefficients = np.linalg.lstsq(design, response, rcond=None)[0]
        residuals = response - design @ coefficients
        return float(residuals @ residuals)
    rss_reduced = residual_sum_squares(reduced, y)
    rss_full = residual_sum_squares(full, y)
    df_arch = len(architectures) - 1
    df_error = n - full.shape[1]
    f_value = (rss_reduced - rss_full) / df_arch / (rss_full / df_error)
    return {'f_value': float(f_value), 'df_architecture': int(df_arch), 'df_error': int(df_error), 'data': data, 'reduced': reduced, 'full': full, 'architectures': architectures, 'seeds': seeds}
