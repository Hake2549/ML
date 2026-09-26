"""หน้าเว็บทำนายการยกเลิกการจองโรงแรม (Streamlit)

รันในเครื่อง:  streamlit run app.py
Deploy:        share.streamlit.io -> เลือก repo นี้ -> main file = app.py
"""
import pandas as pd
import streamlit as st

import predict_core as pc

st.set_page_config(page_title='ทำนายการยกเลิกการจองโรงแรม', layout='wide')


@st.cache_resource
def get_bundle():
    return pc.load_bundle()


bundle = get_bundle()
choices = bundle['choices']
threshold = bundle['threshold']
metrics = bundle['metrics']


def options(col, preferred=None):
    values = list(choices[col])
    if preferred and preferred in values:
        values.remove(preferred)
        values.insert(0, preferred)
    return values


# ---------------- Sidebar ----------------
with st.sidebar:
    st.header('เกี่ยวกับโมเดล')
    st.write(f"**โมเดล:** {bundle['model_name']}")
    st.write(f"**จำนวน features:** {len(bundle['features'])}")
    st.write(f"**Threshold:** {threshold:.2f}")
    st.divider()
    st.subheader('ผลบนชุดทดสอบ')
    st.metric('F1-score', metrics['f1'])
    col_a, col_b = st.columns(2)
    col_a.metric('Precision', metrics['precision'])
    col_b.metric('Recall', metrics['recall'])
    col_a.metric('ROC-AUC', metrics['roc_auc'])
    col_b.metric('PR-AUC', metrics['pr_auc'])
    st.caption(f"ฝึกด้วย {metrics['n_train']:,} แถว · ทดสอบด้วย {metrics['n_test']:,} แถว")
    st.divider()
    st.caption('ข้อมูล: Hotel Booking Demand (Antonio et al., 2019) '
               'โรงแรม 2 แห่งในโปรตุเกส ก.ค. 2015 – ส.ค. 2017 '
               'ผลทำนายอาจไม่ตรงกับโรงแรมในบริบทอื่นหรือช่วงเวลาปัจจุบัน')

# ---------------- Header ----------------
st.title('ทำนายความเสี่ยงที่การจองจะถูกยกเลิก')
st.caption('กรอกรายละเอียดการจอง แล้วกดปุ่มด้านล่างเพื่อดูความน่าจะเป็นที่ลูกค้าจะยกเลิก')

with st.form('booking'):
    st.subheader('รายละเอียดการจอง')
    c1, c2, c3 = st.columns(3)

    with c1:
        arrival_date = st.date_input('วันที่เข้าพัก', value=pd.Timestamp('2017-08-15'))
        lead_time = st.number_input('จองล่วงหน้ากี่วัน (lead time)', min_value=0, max_value=800, value=60)
        total_nights = st.number_input('จำนวนคืนที่พัก', min_value=0, max_value=60, value=3)
        guests = st.number_input('จำนวนผู้เข้าพัก', min_value=1, max_value=20, value=2)

    with c2:
        adr = st.number_input('ราคาห้องต่อคืน (ADR, ยูโร)', min_value=0.0, max_value=1000.0, value=100.0, step=10.0)
        deposit_type = st.selectbox('ประเภทเงินมัดจำ', options('deposit_type', 'No Deposit'))
        market_segment = st.selectbox('กลุ่มตลาด (market segment)', options('market_segment', 'Online TA'))
        customer_type = st.selectbox('ประเภทลูกค้า', options('customer_type', 'Transient'))

    with c3:
        country = st.selectbox('ประเทศของลูกค้า', options('country', 'PRT'),
                               help='PRT = โปรตุเกส (ลูกค้าในประเทศ)')
        agent = st.selectbox('รหัสเอเจนต์ที่จอง', options('agent', 'NoAgent'),
                             help='NoAgent = จองเองโดยไม่ผ่านเอเจนต์')
        total_of_special_requests = st.slider('จำนวนคำขอพิเศษ', 0, 5, 0)
        required_car_parking_spaces = st.slider('จำนวนที่จอดรถที่ขอ', 0, 3, 0)

    st.subheader('ประวัติลูกค้าและการแก้ไขการจอง')
    c4, c5, c6 = st.columns(3)
    previous_cancellations = c4.number_input('เคยยกเลิกมาแล้ว (ครั้ง)', min_value=0, max_value=30, value=0)
    previous_bookings_not_canceled = c5.number_input('เคยจองแล้วไม่ยกเลิก (ครั้ง)', min_value=0, max_value=80, value=0)
    booking_changes = c6.number_input('จำนวนครั้งที่แก้ไขการจอง', min_value=0, max_value=20, value=0)

    submitted = st.form_submit_button('ทำนายผล', type='primary', use_container_width=True)

# ---------------- Result ----------------
if submitted:
    row = pc.build_row(
        bundle, arrival_date=arrival_date, lead_time=lead_time, total_nights=total_nights,
        guests=guests, adr=adr, deposit_type=deposit_type, market_segment=market_segment,
        customer_type=customer_type, country=country, agent=agent,
        total_of_special_requests=total_of_special_requests,
        required_car_parking_spaces=required_car_parking_spaces,
        previous_cancellations=previous_cancellations,
        previous_bookings_not_canceled=previous_bookings_not_canceled,
        booking_changes=booking_changes)
    proba = pc.predict_proba(bundle, row)
    label = pc.risk_label(proba, threshold)

    st.divider()
    left, right = st.columns([1, 2])
    left.metric('ความน่าจะเป็นที่จะยกเลิก', f'{proba:.1%}')
    with right:
        st.progress(min(proba, 1.0))
        if proba >= threshold:
            st.error(f'**{label}** (เกิน threshold {threshold:.2f})')
        elif proba >= threshold * 0.6:
            st.warning(f'**{label}**')
        else:
            st.success(f'**{label}**')

    st.caption('ข้อเสนอแนะ: การจองที่เสี่ยงสูงควรขอมัดจำ ยืนยันการเข้าพักล่วงหน้า '
               'หรือกันห้องสำรองไว้ขายต่อ')

    with st.expander('ดูค่าที่ส่งเข้าโมเดลทั้ง 18 features'):
        st.dataframe(row.T.rename(columns={0: 'ค่า'}), use_container_width=True)
        st.caption('feature ที่คำนวณต่อจากค่าที่กรอก: is_domestic, lead_time_group, '
                   'adr_per_person, cancel_history_ratio, total_nights, '
                   'arrival_date_week_number, arrival_date_day_of_month')
