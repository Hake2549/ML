# Hotel Booking Cancellation Prediction

โปรเจกต์วิชา Machine Learning: ทำนายว่าการจองโรงแรมจะถูกยกเลิกหรือไม่ (Binary Classification)

## โครงสร้าง

| Path | เนื้อหา |
|---|---|
| `hotel_cancellation_training.ipynb` | Notebook หลัก (ใช้บน Google Colab) แบ่งตามหัวข้อรายงาน |
| `data/hotel_bookings.csv` | ข้อมูล 119,390 แถว × 32 คอลัมน์ |
| `outputs/figures/`, `outputs/tables/` | กราฟและตารางหลักฐานสำหรับรายงาน (ชื่อไฟล์ขึ้นต้นด้วยเลขหัวข้อ) |
| `docs/Data-Dictionary.md` | คำอธิบายทุกคอลัมน์ |
| `docs/Project-Plan-7-Days.md` | แผนงาน 7 วัน |

ไฟล์โมเดล (`outputs/models/*.joblib`) ไม่ได้อยู่ใน repo เพราะขนาดเกิน 100 MB ถ้าต้องการโมเดล ให้รัน notebook ใหม่เพื่อสร้างไฟล์

## วิธีรัน

1. เปิด `hotel_cancellation_training.ipynb` ใน Colab
2. อัปโหลด `data/hotel_bookings.csv` ในแถบ Files แล้วตั้ง `DATA_PATH` ใน cell Setup
3. Runtime → Run all (ถ้าต้องการทดสอบให้เร็วขึ้น ตั้ง `QUICK_RUN = True`)

## ที่มาของข้อมูล

- Antonio, N., de Almeida, A., & Nunes, L. (2019). *Hotel booking demand datasets*. Data in Brief, 22, 41–49. https://www.sciencedirect.com/science/article/pii/S2352340918315191
- Kaggle: https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand
