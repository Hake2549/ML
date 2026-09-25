"""สร้างไฟล์ข้อมูลที่มีเฉพาะ 18 คอลัมน์ที่ใช้เทรนจริง + target

รายชื่อ feature อ่านจากผลการคัดเลือกจริง (outputs/tables/5_feature_vote_table.csv)
ไม่ได้พิมพ์ hard-code ไว้ ถ้าคัดเลือกใหม่แล้วผลเปลี่ยน ไฟล์นี้จะเปลี่ยนตาม

วิธีรัน (จาก root ของ repo):  python scripts/make_model_dataset.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
TARGET = 'is_canceled'

votes = pd.read_csv(ROOT / 'outputs' / 'tables' / '5_feature_vote_table.csv', index_col=0)
features = votes.index[votes['decision'] == 'keep'].tolist()

df = pd.read_csv(DATA_DIR / 'hotel_bookings_clean_features.csv')
missing = [c for c in features if c not in df.columns]
assert not missing, f'ไม่พบคอลัมน์เหล่านี้ในไฟล์ข้อมูล: {missing}'

model_df = df[[TARGET] + features]
out = DATA_DIR / 'hotel_bookings_model_18features.csv'
model_df.to_csv(out, index=False, encoding='utf-8-sig')

print(f'rows x cols   : {model_df.shape[0]:,} x {model_df.shape[1]} ({len(features)} features + target)')
print(f'missing values: {int(model_df.isna().sum().sum())}')
print(f'cancel rate   : {model_df[TARGET].mean() * 100:.2f}%')
print(f'saved         : {out}')
print('\nfeatures:')
for i, c in enumerate(features, 1):
    print(f'  {i:2d}. {c:<30} {"numeric" if pd.api.types.is_numeric_dtype(model_df[c]) else "categorical"}')
