"""เทรนโมเดลขนาดเล็กสำหรับนำไป deploy บน Streamlit Community Cloud

ใช้ HistGradientBoosting แทน Random Forest เพราะไฟล์เล็กกว่ามาก (RF = 356.8 MB
ซึ่งเกินลิมิต 100 MB ของ GitHub และกิน RAM เกิน 1 GB ที่ Streamlit ให้)
ค่า hyperparameter มาจากผล tuning จริงใน outputs/tables/7_tuned_params.json

วิธีรัน (จาก root ของ repo):  python scripts/train_deploy_model.py
"""
from pathlib import Path
import json
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (average_precision_score, f1_score, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'hotel_bookings_model_18features.csv'
MODEL_DIR = ROOT / 'models'
MODEL_DIR.mkdir(exist_ok=True)
TARGET = 'is_canceled'
RANDOM_STATE = 42
MIN_FREQ = 50

params = json.loads((ROOT / 'outputs' / 'tables' / '7_tuned_params.json').read_text(encoding='utf-8'))
hgb_params = {k.replace('model__', ''): v for k, v in params['HistGradientBoosting'].items()}
print('hyperparameters:', hgb_params)

df = pd.read_csv(DATA)
features = [c for c in df.columns if c != TARGET]
cat_cols = [c for c in features if not pd.api.types.is_numeric_dtype(df[c])]
num_cols = [c for c in features if c not in cat_cols]
X, y = df[features], df[TARGET]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)
print(f'train {len(X_train):,} | test {len(X_test):,} | features {len(features)}')

pipe = Pipeline([
    ('prep', ColumnTransformer([
        ('num', SimpleImputer(strategy='median'), num_cols),
        ('cat', Pipeline([
            ('impute', SimpleImputer(strategy='most_frequent')),
            ('ordinal', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1,
                                       min_frequency=MIN_FREQ)),
        ]), cat_cols),
    ])),
    ('model', HistGradientBoostingClassifier(random_state=RANDOM_STATE, **hgb_params)),
])

t0 = time.time()
pipe.fit(X_train, y_train)
print(f'fit: {time.time() - t0:.1f}s')

# หา threshold ที่ให้ F1 สูงสุดจาก out-of-fold predictions บน train (ไม่แตะ test set)
oof = cross_val_predict(pipe, X_train, y_train, cv=StratifiedKFold(3, shuffle=True, random_state=RANDOM_STATE),
                        method='predict_proba', n_jobs=-1)[:, 1]
prec, rec, thr = precision_recall_curve(y_train, oof)
f1s = 2 * prec[:-1] * rec[:-1] / np.clip(prec[:-1] + rec[:-1], 1e-12, None)
threshold = float(thr[int(np.argmax(f1s))])
print(f'threshold: {threshold:.4f} (OOF F1 = {f1s.max():.4f})')

proba = pipe.predict_proba(X_test)[:, 1]
pred = (proba >= threshold).astype(int)
metrics = {
    'threshold': round(threshold, 4),
    'f1': round(f1_score(y_test, pred), 4),
    'precision': round(precision_score(y_test, pred), 4),
    'recall': round(recall_score(y_test, pred), 4),
    'roc_auc': round(roc_auc_score(y_test, proba), 4),
    'pr_auc': round(average_precision_score(y_test, proba), 4),
    'n_train': int(len(X_train)), 'n_test': int(len(X_test)),
}
print('test metrics:', metrics)

# ตัวเลือกสำหรับ dropdown ในหน้าเว็บ + ค่ากลางไว้เติมช่องที่ผู้ใช้ไม่กรอก
choices = {c: sorted(df[c].astype(str).value_counts().head(60).index.tolist()) for c in cat_cols}
medians = {c: float(df[c].median()) for c in num_cols}

bundle = {
    'pipeline': pipe, 'features': features, 'cat_cols': cat_cols, 'num_cols': num_cols,
    'threshold': threshold, 'metrics': metrics, 'choices': choices, 'medians': medians,
    'model_name': 'HistGradientBoosting (tuned)', 'params': hgb_params,
}
out = MODEL_DIR / 'hotel_cancel_hgb.joblib'
joblib.dump(bundle, out, compress=3)
print(f'saved: {out} ({out.stat().st_size / 1e6:.2f} MB)')
(MODEL_DIR / 'model_metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
