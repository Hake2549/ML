"""ตรรกะการทำนายที่ใช้ร่วมกันระหว่างหน้าเว็บ (app.py) และการทดสอบ

แยกออกมาจาก app.py เพื่อให้เทสต์ได้โดยไม่ต้องเปิด Streamlit
สูตรของ feature ที่คำนวณต่อ (is_domestic, lead_time_group, adr_per_person,
cancel_history_ratio) ต้องตรงกับที่ใช้ตอนเทรนใน hotel_cancellation_training.ipynb
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent / 'models' / 'hotel_cancel_hgb.joblib'

LEAD_BINS = [-1, 7, 30, 90, 180, 365, np.inf]
LEAD_LABELS = ['0-7', '8-30', '31-90', '91-180', '181-365', '365+']


def load_bundle(path=MODEL_PATH):
    return joblib.load(path)


def lead_time_group(lead_time):
    return LEAD_LABELS[int(np.digitize([lead_time], LEAD_BINS[1:-1], right=True)[0])]


def build_row(bundle, *, arrival_date, lead_time, total_nights, guests, adr, deposit_type,
              market_segment, customer_type, country, agent, total_of_special_requests,
              required_car_parking_spaces, previous_cancellations,
              previous_bookings_not_canceled, booking_changes):
    """สร้างแถวข้อมูล 1 แถวที่มีครบทั้ง 18 คอลัมน์ตามลำดับที่โมเดลคาดหวัง"""
    date = pd.Timestamp(arrival_date)
    past = previous_cancellations + previous_bookings_not_canceled
    guests = max(int(guests), 1)

    values = {
        'deposit_type': deposit_type,
        'agent': str(agent),
        'lead_time': int(lead_time),
        'country': str(country).strip().upper(),
        'total_of_special_requests': int(total_of_special_requests),
        'market_segment': market_segment,
        'adr': float(adr),
        'required_car_parking_spaces': int(required_car_parking_spaces),
        'booking_changes': int(booking_changes),
        'customer_type': customer_type,
        'previous_cancellations': int(previous_cancellations),
        'arrival_date_week_number': int(date.isocalendar()[1]),
        'arrival_date_day_of_month': int(date.day),
        # feature ที่คำนวณต่อ
        'is_domestic': int(str(country).strip().upper() == 'PRT'),
        'lead_time_group': lead_time_group(lead_time),
        'adr_per_person': float(adr) / guests,
        'cancel_history_ratio': (previous_cancellations / past) if past > 0 else 0.0,
        'total_nights': int(total_nights),
    }
    missing = [c for c in bundle['features'] if c not in values]
    assert not missing, f'ยังไม่ได้กำหนดค่าให้ feature: {missing}'
    return pd.DataFrame([values])[bundle['features']]


def predict_proba(bundle, row):
    """คืนความน่าจะเป็นที่การจองนี้จะถูกยกเลิก (0-1)"""
    return float(bundle['pipeline'].predict_proba(row)[0, 1])


def risk_label(proba, threshold):
    if proba >= threshold:
        return 'เสี่ยงสูงที่จะถูกยกเลิก'
    if proba >= threshold * 0.6:
        return 'เสี่ยงปานกลาง'
    return 'เสี่ยงต่ำ'
