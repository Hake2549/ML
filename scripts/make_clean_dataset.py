"""สร้างไฟล์ข้อมูลที่คลีนแล้วจาก data/hotel_bookings.csv
ใช้ขั้นตอนเดียวกับส่วนที่ 2-3 ของ hotel_cancellation_training.ipynb

วิธีรัน (จาก root ของ repo):  python scripts/make_clean_dataset.py
"""
from pathlib import Path
DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
import numpy as np, pandas as pd
MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']
LEAD_BINS=[-1,7,30,90,180,365,np.inf]; LEAD_LABELS=['0-7','8-30','31-90','91-180','181-365','365+']
SEASON={12:'Winter',1:'Winter',2:'Winter',3:'Spring',4:'Spring',5:'Spring',6:'Summer',7:'Summer',8:'Summer',9:'Autumn',10:'Autumn',11:'Autumn'}

raw = pd.read_csv(DATA_DIR / 'hotel_bookings.csv')
df = raw.drop(columns=['reservation_status','reservation_status_date','assigned_room_type'])
df['children'] = df['children'].fillna(0).astype(int)
df['country'] = df['country'].fillna('Unknown')
df['has_agent'] = df['agent'].notna().astype(int)
# ใช้ 'NoAgent' ไม่ใช่ 'None' เพราะ pandas อ่านคำว่า None กลับมาเป็น NaN โดยอัตโนมัติ
df['agent'] = df['agent'].map(lambda v: 'NoAgent' if pd.isna(v) else str(int(v)))
df['has_company'] = df['company'].notna().astype(int)
df = df.drop(columns=['company'])
df['meal'] = df['meal'].replace('Undefined','SC')
df = df[(df['adults']+df['children']+df['babies'])>0]
df = df[(df['adr']>=0)&(df['adr']<=1000)]
df['arrival_date_month'] = df['arrival_date_month'].map({m:i+1 for i,m in enumerate(MONTHS)})
df['arrival_date'] = pd.to_datetime(dict(year=df['arrival_date_year'],month=df['arrival_date_month'],day=df['arrival_date_day_of_month']))
df = df.reset_index(drop=True)
df.to_csv(DATA_DIR / 'hotel_bookings_clean.csv', index=False, encoding='utf-8-sig')
print('clean          :', df.shape, '| missing:', int(df.isna().sum().sum()))

d = df.copy()
d['total_nights'] = d['stays_in_weekend_nights']+d['stays_in_week_nights']
d['total_guests'] = d['adults']+d['children']+d['babies']
d['is_family'] = ((d['children']+d['babies'])>0).astype(int)
d['adr_per_person'] = (d['adr']/d['total_guests'].where(d['total_guests']>0,1)).round(4)
d['lead_time_group'] = pd.cut(d['lead_time'],bins=LEAD_BINS,labels=LEAD_LABELS).astype(str)
past = d['previous_cancellations']+d['previous_bookings_not_canceled']
d['cancel_history_ratio'] = np.where(past>0, d['previous_cancellations']/past.where(past>0,1), 0.0).round(4)
d['season'] = d['arrival_date_month'].map(SEASON)
d['arrival_weekday'] = d['arrival_date'].dt.dayofweek
d['is_domestic'] = (d['country']=='PRT').astype(int)
d.to_csv(DATA_DIR / 'hotel_bookings_clean_features.csv', index=False, encoding='utf-8-sig')
print('clean+features :', d.shape)
print('cancel rate    :', round(d['is_canceled'].mean()*100,2),'%')
print('\ncolumns (clean):'); print(list(df.columns))
print('\nadded features :'); print([c for c in d.columns if c not in df.columns])
