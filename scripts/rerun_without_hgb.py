"""คำนวณผลใหม่หลังตัด Dummy และ HistGradientBoosting ออกจากโครงงาน

1) ตาราง Feature Set A/B/C  ใช้ Random Forest แทน HistGradientBoosting
2) กราฟประสิทธิภาพเทียบจำนวน feature (K) ใช้ Random Forest
3) กราฟเปรียบเทียบโมเดลค่าเริ่มต้น เหลือ 3 โมเดล
4) เทรน Random Forest ฉบับย่อสำหรับเว็บ ให้ไฟล์เล็กพอ deploy ได้

วิธีรัน (จาก root ของ repo):  python scripts/rerun_without_hgb.py
"""
from pathlib import Path
import json
import time

import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (average_precision_score, f1_score, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import (StratifiedKFold, cross_val_predict, cross_validate,
                                     train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

ROOT = Path(__file__).resolve().parent.parent
FIG, TAB = ROOT / 'outputs' / 'figures', ROOT / 'outputs' / 'tables'
TARGET, RANDOM_STATE, MIN_FREQ = 'is_canceled', 42, 50

ORIGINAL = ['hotel', 'lead_time', 'arrival_date_month', 'arrival_date_week_number',
            'arrival_date_day_of_month', 'stays_in_weekend_nights', 'stays_in_week_nights',
            'adults', 'children', 'babies', 'meal', 'country', 'market_segment',
            'distribution_channel', 'is_repeated_guest', 'previous_cancellations',
            'previous_bookings_not_canceled', 'reserved_room_type', 'booking_changes',
            'deposit_type', 'agent', 'has_agent', 'has_company', 'days_in_waiting_list',
            'customer_type', 'adr', 'required_car_parking_spaces', 'total_of_special_requests']
ENGINEERED = ['total_nights', 'total_guests', 'is_family', 'adr_per_person', 'lead_time_group',
              'cancel_history_ratio', 'season', 'arrival_weekday', 'is_domestic']
FEATURES_B = ORIGINAL + ENGINEERED

df = pd.read_csv(ROOT / 'data' / 'hotel_bookings_clean_features.csv')
votes = pd.read_csv(TAB / '5_feature_vote_table.csv', index_col=0)
FEATURES_C = votes.index[votes['decision'] == 'keep'].tolist()
tuned = {k.replace('model__', ''): v for k, v in
         json.loads((TAB / '7_tuned_params.json').read_text(encoding='utf-8'))['RandomForest'].items()}

X_train, X_test, y_train, y_test = train_test_split(
    df[FEATURES_B], df[TARGET], test_size=0.2, stratify=df[TARGET], random_state=RANDOM_STATE)
CV5 = StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE)
CV3 = StratifiedKFold(3, shuffle=True, random_state=RANDOM_STATE)


def make_model(features, **params):
    cat = [c for c in features if not pd.api.types.is_numeric_dtype(df[c])]
    num = [c for c in features if c not in cat]
    prep = ColumnTransformer([
        ('num', SimpleImputer(strategy='median'), num),
        ('cat', Pipeline([('impute', SimpleImputer(strategy='most_frequent')),
                          ('ordinal', OrdinalEncoder(handle_unknown='use_encoded_value',
                                                     unknown_value=-1, min_frequency=MIN_FREQ))]), cat)])
    return Pipeline([('prep', prep),
                     ('model', RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1, **params))])


# ---------------------------------------------------------------- 1) A/B/C ด้วย Random Forest
print('[1/4] เปรียบเทียบ Feature Set A/B/C ด้วย Random Forest ...')
rows = {}
for label, feats in [('A: original', ORIGINAL), ('B: original + engineered', FEATURES_B),
                     ('C: selected', FEATURES_C)]:
    t0 = time.time()
    res = cross_validate(make_model(feats, n_estimators=300), X_train[feats], y_train, cv=CV5,
                         scoring=['f1', 'roc_auc', 'average_precision'], n_jobs=-1)
    rows[label] = {'n_features': len(feats),
                   'f1_mean': res['test_f1'].mean(), 'f1_std': res['test_f1'].std(),
                   'roc_auc_mean': res['test_roc_auc'].mean(), 'roc_auc_std': res['test_roc_auc'].std(),
                   'pr_auc_mean': res['test_average_precision'].mean(),
                   'fit_time_s': res['fit_time'].mean()}
    print(f'   {label}: F1 {rows[label]["f1_mean"]:.4f} ± {rows[label]["f1_std"]:.4f} ({time.time()-t0:.0f}s)')
abc = pd.DataFrame(rows).T.round(4)
abc.to_csv(TAB / '5_feature_set_comparison.csv', encoding='utf-8-sig')

# ---------------------------------------------------------------- 2) performance vs K
print('[2/4] กราฟประสิทธิภาพเทียบจำนวน feature ด้วย Random Forest ...')
ranked = votes.sort_values('mean_rank').index.tolist()
k_values = sorted(set(list(range(3, len(ranked) + 1, 3)) + [len(ranked), len(FEATURES_C)]))
k_rows = []
for k in k_values:
    feats = ranked[:k]
    res = cross_validate(make_model(feats, n_estimators=150), X_train[feats], y_train, cv=CV3,
                         scoring=['f1', 'roc_auc'], n_jobs=-1)
    k_rows.append({'K': k, 'f1_mean': res['test_f1'].mean(), 'f1_std': res['test_f1'].std(),
                   'roc_auc_mean': res['test_roc_auc'].mean()})
    print(f'   K={k:2d}: F1 {k_rows[-1]["f1_mean"]:.4f}')
k_curve = pd.DataFrame(k_rows).set_index('K')
k_curve.round(4).to_csv(TAB / '5_performance_vs_k.csv', encoding='utf-8-sig')

fig, ax = plt.subplots(figsize=(9, 5))
ax.errorbar(k_curve.index, k_curve['f1_mean'], yerr=k_curve['f1_std'], marker='o', capsize=3,
            label='F1 (CV mean ± std)')
ax.axvline(len(FEATURES_C), color='red', ls='--', label=f'Feature Set C (K={len(FEATURES_C)})')
ax.set_xlabel('Number of features K (ordered by mean rank)')
ax.set_ylabel('F1')
ax.set_title('Performance vs number of features (Random Forest, 3-fold CV)')
ax.legend()
plt.tight_layout()
plt.savefig(FIG / '5_performance_vs_k.png', dpi=150)
plt.close()

# ---------------------------------------------------------------- 3) กราฟโมเดลค่าเริ่มต้น 3 โมเดล
print('[3/4] วาดกราฟเปรียบเทียบโมเดลค่าเริ่มต้นใหม่ (3 โมเดล) ...')
KEEP = ['LogisticRegression', 'DecisionTree', 'RandomForest']
defaults = pd.read_csv(TAB / '6_default_models_cv.csv', index_col=0).loc[KEEP]
defaults.to_csv(TAB / '6_default_models_cv.csv', encoding='utf-8-sig')
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(defaults.index, defaults['f1_mean'], yerr=defaults['f1_std'], capsize=4, color='#4C72B0')
ax.set_ylabel('F1 (CV mean ± std)')
ax.set_title('Default models: cross-validated F1')
ax.tick_params(axis='x', rotation=10)
plt.tight_layout()
plt.savefig(FIG / '6_default_models_f1.png', dpi=150)
plt.close()

for name in ('7_before_after_tuning.csv', '7_test_set_results.csv', '7_random_search_HistGradientBoosting.csv'):
    path = TAB / name
    if name.endswith('HistGradientBoosting.csv'):
        path.unlink(missing_ok=True)
        continue
    t = pd.read_csv(path, index_col=0)
    t = t[~t.index.astype(str).str.contains('HistGradientBoosting|Dummy')]
    t.to_csv(path, encoding='utf-8-sig')

# ---------------------------------------------------------------- 4) Random Forest ฉบับย่อสำหรับเว็บ
print('[4/4] เทรน Random Forest ฉบับย่อสำหรับเว็บ ...')
model_df = pd.read_csv(ROOT / 'data' / 'hotel_bookings_model_18features.csv')
feats18 = [c for c in model_df.columns if c != TARGET]
Xd_tr, Xd_te, yd_tr, yd_te = train_test_split(model_df[feats18], model_df[TARGET], test_size=0.2,
                                              stratify=model_df[TARGET], random_state=RANDOM_STATE)
cat18 = [c for c in feats18 if not pd.api.types.is_numeric_dtype(model_df[c])]
num18 = [c for c in feats18 if c not in cat18]


def deploy_pipe(**params):
    prep = ColumnTransformer([
        ('num', SimpleImputer(strategy='median'), num18),
        ('cat', Pipeline([('impute', SimpleImputer(strategy='most_frequent')),
                          ('ordinal', OrdinalEncoder(handle_unknown='use_encoded_value',
                                                     unknown_value=-1, min_frequency=MIN_FREQ))]), cat18)])
    return Pipeline([('prep', prep), ('model', RandomForestClassifier(
        random_state=RANDOM_STATE, n_jobs=-1, class_weight=tuned['class_weight'],
        max_features=tuned['max_features'], **params))])


candidates = [
    dict(n_estimators=100, max_depth=18, min_samples_leaf=20),
    dict(n_estimators=100, max_depth=22, min_samples_leaf=10),
    dict(n_estimators=150, max_depth=25, min_samples_leaf=5),
]
best = None
for params in candidates:
    pipe = deploy_pipe(**params)
    pipe.fit(Xd_tr, yd_tr)
    tmp = ROOT / 'models' / '_tmp.joblib'
    joblib.dump(pipe, tmp, compress=3)
    size_mb = tmp.stat().st_size / 1e6
    proba = pipe.predict_proba(Xd_te)[:, 1]
    f1_at_50 = f1_score(yd_te, (proba >= 0.5).astype(int))
    print(f'   {params} -> {size_mb:.1f} MB | F1(0.50) {f1_at_50:.4f}')
    tmp.unlink()
    if size_mb <= 45 and (best is None or f1_at_50 > best[2]):
        best = (params, pipe, f1_at_50)

params, pipe, _ = best
oof = cross_val_predict(deploy_pipe(**params), Xd_tr, yd_tr, cv=CV3, method='predict_proba', n_jobs=-1)[:, 1]
prec, rec, thr = precision_recall_curve(yd_tr, oof)
f1s = 2 * prec[:-1] * rec[:-1] / np.clip(prec[:-1] + rec[:-1], 1e-12, None)
threshold = float(thr[int(np.argmax(f1s))])
proba = pipe.predict_proba(Xd_te)[:, 1]
pred = (proba >= threshold).astype(int)
metrics = {'threshold': round(threshold, 4), 'f1': round(f1_score(yd_te, pred), 4),
           'precision': round(precision_score(yd_te, pred), 4), 'recall': round(recall_score(yd_te, pred), 4),
           'roc_auc': round(roc_auc_score(yd_te, proba), 4), 'pr_auc': round(average_precision_score(yd_te, proba), 4),
           'n_train': int(len(Xd_tr)), 'n_test': int(len(Xd_te))}
bundle = {'pipeline': pipe, 'features': feats18, 'cat_cols': cat18, 'num_cols': num18,
          'threshold': threshold, 'metrics': metrics, 'model_name': 'Random Forest (ฉบับย่อสำหรับเว็บ)',
          'params': params,
          'choices': {c: sorted(model_df[c].astype(str).value_counts().head(60).index.tolist()) for c in cat18},
          'medians': {c: float(model_df[c].median()) for c in num18}}
out = ROOT / 'models' / 'hotel_cancel_rf_small.joblib'
joblib.dump(bundle, out, compress=3)
(ROOT / 'models' / 'model_metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
print('   params:', params)
print('   metrics:', metrics)
print(f'   saved: {out} ({out.stat().st_size/1e6:.2f} MB)')
print('\nA/B/C ใหม่:')
print(abc[['n_features', 'f1_mean', 'f1_std', 'roc_auc_mean', 'pr_auc_mean', 'fit_time_s']].to_string())
