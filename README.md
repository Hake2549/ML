# Hotel Booking Cancellation Prediction

โปรเจกต์วิชา Machine Learning: ทำนายว่าการจองโรงแรมจะถูกยกเลิกหรือไม่ (Binary Classification)

## โครงสร้าง

| Path | เนื้อหา |
|---|---|
| `hotel_cancellation_training.ipynb` | Notebook หลัก (ใช้บน Google Colab) แบ่งตามหัวข้อรายงาน |
| `data/hotel_bookings.csv` | ข้อมูลดิบ 119,390 แถว × 32 คอลัมน์ |
| `data/hotel_bookings_clean.csv` | ข้อมูลที่คลีนแล้ว 119,208 แถว × 31 คอลัมน์ |
| `data/hotel_bookings_clean_features.csv` | คลีนแล้ว + feature ใหม่ 9 ตัว = 119,208 แถว × 40 คอลัมน์ |
| `data/hotel_bookings_model_18features.csv` | เฉพาะ 18 คอลัมน์ที่ใช้เทรน + target = 119,208 แถว × 19 คอลัมน์ |
| `scripts/make_model_dataset.py` | สร้างไฟล์ 18 คอลัมน์จากผลการคัดเลือก feature จริง |
| `scripts/make_clean_dataset.py` | สร้างไฟล์ที่คลีนแล้วทั้งสองไฟล์ขึ้นใหม่จากข้อมูลดิบ |
| `outputs/figures/`, `outputs/tables/` | กราฟและตารางหลักฐานสำหรับรายงาน (ชื่อไฟล์ขึ้นต้นด้วยเลขหัวข้อ) |
| `docs/Data-Dictionary.md` | คำอธิบายทุกคอลัมน์ |
| `docs/Project-Plan-7-Days.md` | แผนงาน 7 วัน |
| `docs/Slide-Plan.md` | แผนสไลด์นำเสนอ 17 หน้า + แบ่งเวลาและผู้พูด |

ไฟล์โมเดล (`outputs/models/*.joblib`) ไม่ได้อยู่ใน repo เพราะขนาดเกิน 100 MB ถ้าต้องการโมเดล ให้รัน notebook ใหม่เพื่อสร้างไฟล์

## วิธีรัน

1. เปิด `hotel_cancellation_training.ipynb` ใน Colab
2. อัปโหลด `data/hotel_bookings.csv` ในแถบ Files แล้วตั้ง `DATA_PATH` ใน cell Setup
3. Runtime → Run all (ถ้าต้องการทดสอบให้เร็วขึ้น ตั้ง `QUICK_RUN = True`)

## ที่มาของข้อมูล

- Antonio, N., de Almeida, A., & Nunes, L. (2019). *Hotel booking demand datasets*. Data in Brief, 22, 41–49. https://www.sciencedirect.com/science/article/pii/S2352340918315191
- Kaggle: https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand
