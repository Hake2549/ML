"""ตรวจว่าอันดับ Feature Importance ของ Random Forest เปลี่ยนไหม เมื่อลด overfitting

เทียบ 2 แบบบน train set เดียวกัน (Feature Set B = 37 features)
  A = ค่าที่ใช้ตอนคัดเลือกจริงในรายงาน (min_samples_leaf=5)
  B = พารามิเตอร์ที่ผ่าน hyperparameter tuning แล้ว (gap train-CV ต่ำกว่า)
ถ้าอันดับแทบไม่เปลี่ยน = อคติจาก overfitting ไม่ได้ทำให้ชุด feature สุดท้ายเพี้ยน

วิธีรัน (จาก root ของ repo):  python scripts/compare_rf_importance.py
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

ROOT = Path(__file__).resolve().parent.parent
TARGET = 'is_canceled'
RANDOM_STATE = 42
MIN_FREQ = 50
TOP_N = 18

ORIGINAL_FEATURES = ['hotel', 'lead_time', 'arrival_date_month', 'arrival_date_week_number',
                     'arrival_date_day_of_month', 'stays_in_weekend_nights', 'stays_in_week_nights',
                     'adults', 'children', 'babies', 'meal', 'country', 'market_segment',
                     'distribution_channel', 'is_repeated_guest', 'previous_cancellations',
                     'previous_bookings_not_canceled', 'reserved_room_type', 'booking_changes',
                     'deposit_type', 'agent', 'has_agent', 'has_company', 'days_in_waiting_list',
                     'customer_type', 'adr', 'required_car_parking_spaces', 'total_of_special_requests']
ENGINEERED = ['total_nights', 'total_guests', 'is_family', 'adr_per_person', 'lead_time_group',
              'cancel_history_ratio', 'season', 'arrival_weekday', 'is_domestic']
FEATURES = ORIGINAL_FEATURES + ENGINEERED

df = pd.read_csv(ROOT / 'data' / 'hotel_bookings_clean_features.csv')
X_train, _, y_train, _ = train_test_split(df[FEATURES], df[TARGET], test_size=0.2,
                                          stratify=df[TARGET], random_state=RANDOM_STATE)
cat_cols = [c for c in FEATURES if not pd.api.types.is_numeric_dtype(df[c])]
num_cols = [c for c in FEATURES if c not in cat_cols]
print(f'train {len(X_train):,} แถว | {len(FEATURES)} features ({len(cat_cols)} categorical)')

tuned = {k.replace('model__', ''): v for k, v in
         json.loads((ROOT / 'outputs' / 'tables' / '7_tuned_params.json').read_text(encoding='utf-8'))['RandomForest'].items()}
SETTINGS = {
    'A_report (min_samples_leaf=5)': dict(n_estimators=300, min_samples_leaf=5),
    'B_tuned': tuned,
}
print('B_tuned =', tuned)


def make_pipe(params):
    prep = ColumnTransformer([
        ('num', SimpleImputer(strategy='median'), num_cols),
        ('cat', Pipeline([('impute', SimpleImputer(strategy='most_frequent')),
                          ('ordinal', OrdinalEncoder(handle_unknown='use_encoded_value',
                                                     unknown_value=-1, min_frequency=MIN_FREQ))]), cat_cols),
    ])
    rf = RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1, **params)
    return Pipeline([('prep', prep), ('model', rf)])


scores, importances = {}, {}
for name, params in SETTINGS.items():
    pipe = make_pipe(params)
    cv = cross_validate(pipe, X_train, y_train, cv=StratifiedKFold(3, shuffle=True, random_state=RANDOM_STATE),
                        scoring='f1', n_jobs=-1, return_train_score=True)
    pipe.fit(X_train, y_train)
    importances[name] = pd.Series(pipe.named_steps['model'].feature_importances_, index=num_cols + cat_cols)
    scores[name] = {'cv_f1': cv['test_score'].mean(), 'train_f1': cv['train_score'].mean(),
                    'gap': cv['train_score'].mean() - cv['test_score'].mean()}
    print(f"{name}: CV F1 {scores[name]['cv_f1']:.4f} | train F1 {scores[name]['train_f1']:.4f} | gap {scores[name]['gap']:.4f}")

imp = pd.DataFrame(importances)
ranks = imp.rank(ascending=False)
ranks.columns = [f'rank_{c.split("_")[0]}' for c in ranks.columns]
result = pd.concat([imp.round(5), ranks], axis=1).sort_values(ranks.columns[0])
result['rank_change'] = (result[ranks.columns[1]] - result[ranks.columns[0]]).astype(int)
result['in_top18_A'] = result[ranks.columns[0]] <= TOP_N
result['in_top18_B'] = result[ranks.columns[1]] <= TOP_N
result.to_csv(ROOT / 'outputs' / 'tables' / '5_rf_importance_tuned_vs_default.csv', encoding='utf-8-sig')

rho = spearmanr(ranks.iloc[:, 0], ranks.iloc[:, 1]).statistic
overlap = (result['in_top18_A'] & result['in_top18_B']).sum()
changed = result[result['in_top18_A'] != result['in_top18_B']]
print(f'\nSpearman ของอันดับ A vs B = {rho:.4f}')
print(f'Top-{TOP_N} ตรงกัน {overlap}/{TOP_N} ตัว')
print('เข้า/ออก Top-18 ต่างกัน:', changed.index.tolist() if len(changed) else 'ไม่มีเลย')
print('\n10 อันดับแรกของแต่ละแบบ')
print('A:', ranks.sort_values(ranks.columns[0]).index[:10].tolist())
print('B:', ranks.sort_values(ranks.columns[1]).index[:10].tolist())

fig, ax = plt.subplots(figsize=(7, 7))
ax.scatter(ranks.iloc[:, 0], ranks.iloc[:, 1], s=28)
lim = len(FEATURES) + 1
ax.plot([0, lim], [0, lim], ls='--', c='grey', lw=1)
ax.axvline(TOP_N + 0.5, c='red', ls=':', lw=1)
ax.axhline(TOP_N + 0.5, c='red', ls=':', lw=1)
for f in ranks.index:
    if abs(ranks.loc[f].iloc[0] - ranks.loc[f].iloc[1]) >= 3:
        ax.annotate(f, (ranks.loc[f].iloc[0], ranks.loc[f].iloc[1]), fontsize=7,
                    xytext=(3, 3), textcoords='offset points')
ax.set_xlabel('Rank - report setting (min_samples_leaf=5)')
ax.set_ylabel('Rank - tuned setting')
ax.set_title(f'RF feature importance ranks: report vs tuned (Spearman = {rho:.3f})')
plt.tight_layout()
plt.savefig(ROOT / 'outputs' / 'figures' / '5_rf_importance_tuned_vs_default.png', dpi=150)
print('\nsaved table + figure')
