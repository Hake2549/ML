# 📅 แผนงาน 7 วัน: Hotel Booking Cancellation Prediction

**ช่วงเวลา:** เสาร์ 19 ก.ย. – ศุกร์ 25 ก.ย. 2569
**Dataset:** [Hotel booking demand — Kaggle (jessemostipak)](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand) · ไฟล์ `hotel_bookings.csv` (119,390 แถว × 32 คอลัมน์)
**อ้างอิงที่มาข้อมูล:** Antonio, N., de Almeida, A., & Nunes, L. (2019). *Hotel booking demand datasets*. Data in Brief, 22, 41–49.

> ✅ **สถานะไฟล์ข้อมูล (อัปเดต 20 ก.ย.):** ได้ไฟล์เต็ม `hotel_bookings.csv` แล้ว (119,390 แถว × 32 คอลัมน์) อยู่ในโฟลเดอร์ `data/`

---

## สิ่งที่ต้องส่ง

| # | ชิ้นงาน | หมายเหตุ | สถานะ |
|---|---|---|---|
| 1 | **Colab Notebook** | โค้ดทั้งหมดอยู่ที่นี่ (รายงานไม่ต้องมีโค้ด) | ⬜ |
| 2 | **รายงาน** | ใช้รูปแบบใน Google Docs ของอาจารย์ | ⬜ |
| 3 | **สไลด์นำเสนอ** | 6 หัวข้อ เน้นผลลัพธ์ การอธิบาย และการอภิปรายผล | ⬜ |
| 4 | **เว็บ** | ไม่บังคับ | ⬜ |

## หลักการวางแผน

- **ให้เวลากับหัวข้อ 5 และ 7 มากที่สุด** (รวมประมาณ 3 จาก 7 วัน) เพราะอาจารย์เน้น 2 หัวข้อนี้
- **เขียนรายงานไปพร้อมกับรันโค้ด** ทำส่วนไหนเสร็จก็เขียนส่วนนั้นทันที ไม่รอเขียนรวดเดียวตอนท้าย
- **บันทึกกราฟและตารางทุกชิ้นลง Google Drive ตั้งแต่วันแรก** จะได้ใช้ทั้งในรายงานและสไลด์
- **จัดโครงสร้าง Colab ให้ตรงกับหัวข้อรายงาน** อาจารย์จะเปิดเทียบกันได้ง่าย
- **ห้ามแต่งตัวเลข** ทุกตัวเลขในรายงานต้องมาจากผลการรันจริง

---

## วันที่ 1 (เสาร์ 19): เตรียมงาน + Problem & Data Understanding

**Colab**
- [ ] ดาวน์โหลดไฟล์เต็ม `hotel_bookings.csv` แล้วอัปโหลดขึ้น Google Drive
- [ ] สร้าง Notebook แบ่ง section ให้ตรงกับหัวข้อรายงาน และเชื่อม Google Drive
- [ ] ดูขนาดข้อมูล ชนิดข้อมูล และ**ตาราง missing value รายคอลัมน์**
- [ ] ดูสัดส่วนคลาสของ `is_canceled` (คาดว่าราว 37:63)
- [ ] EDA: อัตรายกเลิกแยกตามประเภทโรงแรม, `lead_time`, `deposit_type`, ช่องทางการจอง และเดือน
- [ ] หาจุดผิดปกติ เช่น `adr` ติดลบหรือสูงเกินจริง และแถวที่จำนวนผู้เข้าพักเป็น 0
- [ ] ระบุคอลัมน์ที่ทำให้เกิด leakage

**รายงาน**
- [ ] ร่างหัวข้อ 1–3 (Introduction, Problem Definition, Dataset Description)

**เสร็จเมื่อ:** มีตาราง missing value, กราฟสัดส่วนคลาส และกราฟ EDA อย่างน้อย 4 รูป

> 💡 วันนี้ควรแจ้งอาจารย์ล็อกหัวข้อไว้ก่อน กันซ้ำกับเพื่อน

---

## วันที่ 2 (อาทิตย์ 20): Data Preparation + Baseline

**Colab**
- [ ] ตัดคอลัมน์ leakage (`reservation_status`, `reservation_status_date`) และ**ตรวจ `assigned_room_type`** ด้วย
- [ ] จัดการ missing value
  - [ ] `company` และ `agent`: แปลงเป็น flag ว่า "มี/ไม่มี"
  - [ ] `country`: แทนค่าว่างด้วย "Unknown"
  - [ ] `children`: แทนค่าว่างด้วย 0
- [ ] ลบแถวผิดปกติ และจดไว้ว่าลบไปกี่แถว ด้วยเหตุผลอะไร
- [ ] **แบ่ง Train/Test ก่อนทำขั้นตอนอื่น** โดยทำ 2 แบบ
  - [ ] (a) Stratified Random Split
  - [ ] (b) Time-based Split
- [ ] สร้าง Pipeline ที่รวม encoding และ scaling ไว้ในตัว
- [ ] รัน **Dummy Classifier** และ **Logistic Regression** เพื่อเช็กว่า Pipeline ทำงานถูกต้อง

**รายงาน**
- [ ] หัวข้อ 4 (Data Preparation) พร้อมตาราง "ปัญหาที่พบ → วิธีจัดการ → เหตุผล"

**เสร็จเมื่อ:** Pipeline รันได้ และมีคะแนน Baseline ไว้เทียบ

---

## วันที่ 3 (จันทร์ 21): ⭐ Feature Engineering & Selection (หัวข้อ 5)

**Colab**
- [ ] สร้าง feature ใหม่ 6–8 ตัว และเขียนสมมติฐานของแต่ละตัว
  - `total_nights`, `total_guests`, `is_family`, `adr_per_person`
  - `lead_time_group`, `cancel_history_ratio`, `season`, `is_domestic`
- [ ] ทำกราฟ**อัตรายกเลิกแยกตามกลุ่ม**ของ feature ใหม่ทุกตัว เพื่อพิสูจน์สมมติฐาน
- [ ] คัดเลือก feature ด้วย 3 วิธี
  - [ ] Filter: Correlation Heatmap + Mutual Information (SelectKBest)
  - [ ] Embedded: Random Forest Feature Importance
  - [ ] Model-agnostic: Permutation Importance
- [ ] ทำ**ตารางโหวต** แล้วเก็บ feature ที่ผ่านอย่างน้อย 2 ใน 3 วิธี
- [ ] ทำ**กราฟประสิทธิภาพเทียบกับจำนวน feature (K)**
- [ ] ทำ**ตารางเปรียบเทียบชุด A/B/C** โดยใช้โมเดลเดียวกันและ CV แบบเดียวกัน
  - A = feature เดิม (ตัด leakage แล้ว)
  - B = A + feature ใหม่
  - C = feature ที่คัดเลือกแล้ว

**รายงาน**
- [ ] เขียนหัวข้อ 5 ให้เสร็จภายในวันนี้

**เสร็จเมื่อ:** มีกราฟหรือตารางตั้งแต่ 7 ชิ้นขึ้นไป และตอบได้ว่า "ทำไมเลือก K เท่านี้"

---

## วันที่ 4 (อังคาร 22): Model Development + เริ่ม Tuning (หัวข้อ 6–7)

**Colab**
- [ ] Train ครบ 5 โมเดลด้วยค่า default พร้อม Stratified 5-Fold CV (ใช้เฉพาะ Train set)
  - Dummy · Logistic Regression · Decision Tree · Random Forest · Gradient Boosting
- [ ] บันทึก F1, ROC-AUC และ PR-AUC ในรูป **mean ± std**
- [ ] ทำ **RandomizedSearchCV** กับ Random Forest และ Gradient Boosting
- [ ] บันทึกผล tuning ลง Drive ทันที เพราะ Colab หลุดการเชื่อมต่อบ่อย

**รายงาน**
- [ ] หัวข้อ 6 (โมเดลที่เลือกและเหตุผล)
- [ ] ตารางช่วง hyperparameter ที่ทดลอง

**เสร็จเมื่อ:** มีตารางผลก่อน tuning ครบทุกโมเดล

---

## วันที่ 5 (พุธ 23): ⭐ Evaluation & Tuning เชิงลึก (หัวข้อ 7)

**Colab**
- [ ] ทำ GridSearchCV แบบละเอียด รอบค่าที่ดีที่สุดจากเมื่อวาน
- [ ] ทำ **Validation Curve** (เช่น `max_depth`) และ **Learning Curve**
- [ ] ทำ**ตารางก่อน–หลัง tuning** และใส่ช่องว่างระหว่างคะแนน Train กับ Test ด้วย
- [ ] ทำ **Threshold Tuning** จาก PR Curve (หาค่าจาก validation เท่านั้น)
- [ ] **ประเมินบน Test set เพียงครั้งเดียว** แล้วทำ Confusion Matrix
- [ ] เทียบผล **Random Split กับ Time-based Split**
- [ ] ทำ Error Analysis แยกตามประเภทโรงแรมและช่องทางการจอง
- [ ] เลือกโมเดลสุดท้าย แล้ว save เป็นไฟล์ `.joblib`

**รายงาน**
- [ ] เขียนหัวข้อ 7 ให้ครบ ทั้งจุดแข็ง จุดอ่อน สาเหตุ และการเปรียบเทียบโมเดล

**เสร็จเมื่อ:** ตอบได้ว่า "tuning แล้วดีขึ้นจริงไหม" และ "ทำไมเลือกโมเดลนี้"

---

## วันที่ 6 (พฤหัส 24): Deploy + ปิดรายงาน

**Deploy (เลือก 1 แบบ)**

| แบบ | ความยาก | หมายเหตุ |
|---|---|---|
| **Gradio ใน Colab** ✅ แนะนำ | ง่าย | รันจาก Colab ได้ทันที และได้ลิงก์ demo แบบชั่วคราว |
| Streamlit Community Cloud | ปานกลาง | ได้เว็บถาวร ใช้เป็นชิ้นงานข้อ 4 ได้ แต่ต้องใช้ GitHub |

- [ ] ทำฟอร์มกรอกข้อมูลการจอง ให้แสดงความน่าจะเป็นที่การจองจะถูกยกเลิก
- [ ] เก็บตัวอย่าง input → output ไว้ 2–3 เคส เช่น เสี่ยงสูงกับเสี่ยงต่ำ

**รายงาน**
- [ ] เขียนหัวข้อ 8–10 (Deployment, Conclusion, References)
- [ ] กลับไปขัดเกลาหัวข้อ 5 และ 7 อีกรอบ

**เสร็จเมื่อ:** รายงานครบ 10 หัวข้อ และ demo ใช้งานได้

---

## วันที่ 7 (ศุกร์ 25): สไลด์ + ซ้อม + ตรวจความเรียบร้อย

**สไลด์ประมาณ 14 หน้า** (เน้นผลลัพธ์ การอธิบาย และการอภิปรายผล)

| หัวข้อสไลด์ | จำนวนหน้า | เนื้อหาหลัก |
|---|---|---|
| Problem & Data Understanding | 2 | ที่มาของปัญหา, ขนาดข้อมูล, สัดส่วนคลาส |
| Data Preparation | 2 | ตารางปัญหาและวิธีแก้, เรื่อง leakage |
| **Feature Engineering & Selection** | **3** | feature ใหม่, ตารางโหวต, ตาราง A/B/C |
| Model Development | 1 | 5 โมเดลและเหตุผลที่เลือก |
| **Model Evaluation & Tuning** | **4** | ก่อน–หลัง tuning, curves, Random vs Time split, Confusion Matrix |
| Deploy | 1 | demo หรือภาพหน้าจอ |
| สรุป + ข้อจำกัด | 1 | ตอบโจทย์หรือไม่, สิ่งที่ได้เรียนรู้ |

- [ ] ทำสไลด์
- [ ] ซ้อมนำเสนอและจับเวลา
- [ ] เตรียมคำตอบสำหรับคำถามที่น่าจะโดนถาม: ข้อมูลเก่าไปไหม? ใช้กับไทยได้ไหม? ทำไมไม่ใช้ Accuracy? ทำไมเลือกค่า hyperparameter นี้?
- [ ] **ตั้งสิทธิ์แชร์ Colab และ Docs เป็น "ทุกคนที่มีลิงก์ดูได้"**
- [ ] Restart runtime แล้วกด Run all ใน Colab ใหม่ทั้งหมด เพื่อยืนยันว่ารันได้ตั้งแต่ต้นจนจบ

---

## ⚠️ ความเสี่ยงและทางแก้

| ความเสี่ยง | ทางแก้ |
|---|---|
| Colab หลุดระหว่าง tuning | บันทึกผลลง Drive ทุกขั้น ลด `n_iter` หรือใช้ข้อมูลตัวอย่าง 30% ในรอบค้นหาแบบกว้าง |
| Tuning ใช้เวลานาน | ใช้ `HistGradientBoosting` ซึ่งเร็วกว่า Gradient Boosting แบบปกติมาก |
| Tuning แล้วผลดีขึ้นแค่นิดเดียว | รายงานตามจริง แล้วอธิบายผ่านช่องว่างระหว่าง Train กับ Test แทน |
| งานล่าช้า | วันที่ 6 และ 7 ใช้เป็นเวลาสำรองได้ ส่วนเว็บเป็นงานเสริมที่ตัดออกได้ก่อน |

**ถ้าทำไม่ทันจริงๆ ให้ตัดตามลำดับนี้:** เว็บถาวร → Threshold Tuning → Learning Curve

**ห้ามตัด:** Baseline, ตาราง A/B/C และตารางก่อน–หลัง tuning เพราะเป็นหลักฐานหลักของหัวข้อ 5 และ 7

---

## 📎 Checklist หลักฐานที่ต้องแนบในรายงาน

**หัวข้อ 5**
- [ ] กราฟอัตรายกเลิกของ feature ใหม่แต่ละตัว
- [ ] Correlation Heatmap
- [ ] กราฟ Mutual Information
- [ ] กราฟ Random Forest Importance
- [ ] กราฟ Permutation Importance
- [ ] ตารางโหวต
- [ ] กราฟประสิทธิภาพ vs K
- [ ] ตารางเปรียบเทียบชุด A/B/C

**หัวข้อ 7**
- [ ] ผล Baseline (Dummy)
- [ ] ตารางช่วง Hyperparameter
- [ ] Validation Curve
- [ ] Learning Curve
- [ ] ตารางก่อน–หลัง Tuning
- [ ] ผล Random Split vs Time-based Split
- [ ] PR Curve + Threshold
- [ ] Confusion Matrix
- [ ] ตาราง Error Analysis
- [ ] ตารางเปรียบเทียบโมเดลสุดท้าย
