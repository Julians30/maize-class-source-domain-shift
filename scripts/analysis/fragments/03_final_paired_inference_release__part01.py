#!/usr/bin/env python3


"""Release-safe analytical source reconstructed from the frozen project notebook.

This file preserves the notebook code sequence while removing execution outputs,
Colab-only metadata, and private absolute paths. Runtime paths are parameterized.
"""


'Final paired inference and publication-ready analytical outputs\n\nRelease-safe Python export derived from the executed manuscript-facing paired-inference notebook.\nNotebook outputs and Colab identity metadata are intentionally excluded.\n'


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


import zipfile


import numpy as np


import pandas as pd


import matplotlib.pyplot as plt


from sklearn.metrics import confusion_matrix, f1_score, accuracy_score, balanced_accuracy_score, matthews_corrcoef


REPO_ROOT = Path(os.environ.get('MAIZE_REPO_ROOT', '.')).resolve()


E2_ROOT = Path(os.environ.get('MAIZE_E2_ROOT', REPO_ROOT / 'predictions' / 'internal_E2A')).resolve()


OUTPUT_DIR = Path(os.environ.get('MAIZE_OUTPUT_DIR', REPO_ROOT / 'results' / 'reproduction' / 'final_paired_inference')).resolve()


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


ARCHITECTURES = {'EfficientNet-B0': 'efficientnet_b0', 'MobileNetV3-Large': 'mobilenetv3_large', 'MobileViT-S': 'mobilevit_s', 'ResNet50': 'resnet50', 'Swin-Tiny': 'swin_tiny_patch4_window7_224', 'ViT-Base/16': 'vit_base_patch16_224'}


SEEDS = [17, 42, 73]


EXPECTED_N = 1719


EXPECTED_CLASSES = ['fall_armyworm', 'grasshopper', 'healthy', 'leaf_beetle', 'leaf_blight', 'leaf_spot', 'lethal_necrosis', 'rust', 'streak_virus']


N_CLASSES = len(EXPECTED_CLASSES)


N_BOOTSTRAP = 10000


RANDOM_SEED = 20260803


print('E2 prediction root:', E2_ROOT)


print('OUTPUT_DIR:', OUTPUT_DIR)


def probability_columns(df):
    return sorted([column for column in df.columns if column.startswith('prob_')], key=lambda column: int(column.split('_')[1]))


def metrics_from_confusion(confusion):
    true_positive = np.diag(confusion).astype(float)
    predicted_total = confusion.sum(axis=0).astype(float)
    true_total = confusion.sum(axis=1).astype(float)
    precision = np.divide(true_positive, predicted_total, out=np.zeros_like(true_positive), where=predicted_total > 0)
    recall = np.divide(true_positive, true_total, out=np.zeros_like(true_positive), where=true_total > 0)
    class_f1 = np.divide(2.0 * precision * recall, precision + recall, out=np.zeros_like(true_positive), where=precision + recall > 0)
    return {'macro_f1': float(class_f1.mean()), 'balanced_accuracy': float(recall.mean()), 'class_f1': class_f1, 'class_recall': recall, 'class_precision': precision}


def percentile_interval(values, alpha=0.05):
    return np.quantile(values, [alpha / 2.0, 1.0 - alpha / 2.0])


def bootstrap_two_sided_p(differences):
    lower_tail = np.mean(differences <= 0.0)
    upper_tail = np.mean(differences >= 0.0)
    return float(min(1.0, 2.0 * min(lower_tail, upper_tail)))


def holm_adjust(p_values):
    p_values = np.asarray(p_values, dtype=float)
    order = np.argsort(p_values)
    adjusted = np.empty_like(p_values)
    running_maximum = 0.0
    number = len(p_values)
    for rank, index in enumerate(order):
        candidate = (number - rank) * p_values[index]
        running_maximum = max(running_maximum, candidate)
        adjusted[index] = min(1.0, running_maximum)
    return adjusted


def exact_aurc(correct, confidence):
    order = np.argsort(-confidence)
    errors = (~correct[order]).astype(float)
    cumulative_risk = np.cumsum(errors) / np.arange(1, len(errors) + 1)
    coverage = np.arange(1, len(errors) + 1) / len(errors)
    area = np.trapz(cumulative_risk, coverage)
    return (float(area), coverage, cumulative_risk)


def equal_frequency_reliability(correct, confidence, n_bins=10):
    frame = pd.DataFrame({'correct': correct.astype(int), 'confidence': confidence.astype(float)})
    frame['bin'] = pd.qcut(frame['confidence'], q=n_bins, labels=False, duplicates='drop')
    return frame.groupby('bin', observed=True).agg(n=('correct', 'size'), mean_confidence=('confidence', 'mean'), observed_accuracy=('correct', 'mean')).reset_index()


def save_figure(figure, stem):
    png_path = OUTPUT_DIR / f'{stem}.png'
    pdf_path = OUTPUT_DIR / f'{stem}.pdf'
    figure.savefig(png_path, dpi=300, bbox_inches='tight')
    figure.savefig(pdf_path, bbox_inches='tight')
    plt.close(figure)
    return (png_path, pdf_path)


runs = {}


validation_rows = []


reference_keys = None
