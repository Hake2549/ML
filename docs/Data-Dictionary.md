# 📖 Data Dictionary — Hotel Booking Demand (32 คอลัมน์)

**Dataset:** [Hotel booking demand — Kaggle (jessemostipak)](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand) · ไฟล์ `hotel_bookings.csv` · 119,390 แถว × 32 คอลัมน์
**คำอธิบายตัวแปรอ้างอิงจาก:** Antonio, N., de Almeida, A., & Nunes, L. (2019). *Hotel booking demand datasets*. **Data in Brief**, 22, 41–49. (ตารางที่ 1) — [อ่านฉบับเต็ม](https://pmc.ncbi.nlm.nih.gov/articles/PMC6297060/)

**สรุปจำนวน feature**

| ขั้น | จำนวน |
|---|---|
| คอลัมน์ทั้งหมด | 32 |
| ตัด target (`is_canceled`) | 31 |
| ตัด leakage (`reservation_status`, `reservation_status_date`) | 29 |
| ตัด `assigned_room_type` เพิ่ม (ถ้าตรวจแล้วพบว่า leak) | 28 |
| รวม feature ที่สร้างใหม่ 9 ตัว | ~37 (ก่อนคัดเลือก) |

---

## 🏨 1. ข้อมูลโรงแรมและผลลัพธ์

| คอลัมน์ | ชนิด | ความหมาย | ค่าที่พบ | การจัดการใน Notebook |
|---|---|---|---|---|
| `hotel` | Categorical | ประเภทโรงแรม | `Resort Hotel`, `City Hotel` | ใช้ |
| **`is_canceled`** 🎯 | Binary | **Target**: การจองถูกยกเลิกหรือไม่ | `1` = ยกเลิก, `0` = ไม่ยกเลิก | สิ่งที่ต้องทำนาย |

> คอลัมน์ `hotel` **ไม่มีในเปเปอร์** เพราะเปเปอร์แยกข้อมูลเป็น 2 ชุด (H1 = Resort Hotel 40,060 แถว, H2 = City Hotel 79,330 แถว)
> เวอร์ชันบน Kaggle รวม 2 ชุดเข้าด้วยกันแล้วเพิ่มคอลัมน์นี้ขึ้นมา **ตัวแปรในเปเปอร์จึงมี 31 ตัว แต่บน Kaggle มี 32**

---

## 📅 2. เวลาการจองและการเข้าพัก

| คอลัมน์ | ชนิด | ความหมาย | ค่าที่พบ | การจัดการใน Notebook |
|---|---|---|---|---|
| `lead_time` | Integer | **จำนวนวันระหว่างวันที่บันทึกการจองเข้าระบบ กับวันที่เข้าพัก** | 0 ถึงหลายร้อยวัน | ใช้ + สร้าง `lead_time_group` |
| `arrival_date_year` | Integer | ปีที่เข้าพัก | 2015, 2016, 2017 | **ไม่ใช้เป็น feature** (ปีในอนาคตไม่มีในข้อมูล train) |
| `arrival_date_month` | Categorical | เดือนที่เข้าพัก | `January` – `December` | แปลงเป็นตัวเลข 1–12 + สร้าง `season` |
| `arrival_date_week_number` | Integer | สัปดาห์ของปีที่เข้าพัก | 1–53 | ใช้ |
| `arrival_date_day_of_month` | Integer | วันที่ของเดือนที่เข้าพัก | 1–31 | ใช้ + สร้าง `arrival_weekday` |
| `stays_in_weekend_nights` | Integer | จำนวนคืนวันหยุด (เสาร์–อาทิตย์) ที่พักหรือจองไว้ | 0, 1, 2, … | ใช้ + สร้าง `total_nights` |
| `stays_in_week_nights` | Integer | จำนวนคืนวันธรรมดา (จันทร์–ศุกร์) ที่พักหรือจองไว้ | 0, 1, 2, … | ใช้ + สร้าง `total_nights` |

---

## 👨‍👩‍👧 3. ผู้เข้าพัก

| คอลัมน์ | ชนิด | ความหมาย | ค่าที่พบ | การจัดการใน Notebook |
|---|---|---|---|---|
| `adults` | Integer | จำนวนผู้ใหญ่ | 0, 1, 2, … | ใช้ |
| `children` | Integer | จำนวนเด็ก (ทั้งแบบเสียเงินและไม่เสียเงิน) | 0, 1, 2, … | ⚠️ missing 4 ค่า → เติม 0 |
| `babies` | Integer | จำนวนทารก | 0, 1, … | ใช้ + สร้าง `total_guests`, `is_family` |

> แถวที่ `adults + children + babies = 0` คือการจองที่ไม่มีผู้เข้าพัก ถือว่าเป็นข้อมูลผิดปกติ → Notebook ลบทิ้ง

---

## 🧑 4. ข้อมูลลูกค้า

| คอลัมน์ | ชนิด | ความหมาย | ค่าที่พบ | การจัดการใน Notebook |
|---|---|---|---|---|
| `country` | Categorical | ประเทศต้นทางของลูกค้า (รหัส 3 ตัวอักษร) | `PRT`, `GBR`, `FRA`, … | ⚠️ missing 488 ค่า → `Unknown` + สร้าง `is_domestic` |
| `customer_type` | Categorical | ประเภทลูกค้า | `Transient` (รายบุคคล), `Transient-Party` (รายบุคคลที่เชื่อมกับการจองอื่น), `Contract` (มีสัญญา), `Group` (กลุ่ม) | ใช้ |
| `is_repeated_guest` | Binary | ชื่อผู้จองเคยเข้าพักมาก่อนหรือไม่ | `1` = ลูกค้าเก่า, `0` = ใหม่ | ใช้ |
| `previous_cancellations` | Integer | จำนวนครั้งที่ลูกค้าเคย**ยกเลิก**ก่อนการจองนี้ | 0, 1, 2, … | ใช้ + สร้าง `cancel_history_ratio` |
| `previous_bookings_not_canceled` | Integer | จำนวนครั้งที่ลูกค้าเคยจอง**โดยไม่ยกเลิก**ก่อนการจองนี้ | 0, 1, 2, … | ใช้ + สร้าง `cancel_history_ratio` |

---

## 📞 5. ช่องทางการจอง

| คอลัมน์ | ชนิด | ความหมาย | ค่าที่พบ | การจัดการใน Notebook |
|---|---|---|---|---|
| `market_segment` | Categorical | กลุ่มตลาดของการจอง | `Online TA`, `Offline TA/TO`, `Groups`, `Direct`, `Corporate`, `Complementary`, `Aviation` | ใช้ |
| `distribution_channel` | Categorical | ช่องทางที่ได้การจองมา | `TA/TO`, `Direct`, `Corporate`, `GDS` | ใช้ |
| `agent` | Categorical | **รหัส ID** ของบริษัททัวร์/เอเจนต์ที่ทำการจอง | 9, 240, 1, … | ⚠️ missing 16,340 → `None` + flag `has_agent` |
| `company` | Categorical | **รหัส ID** ของบริษัท/องค์กรที่ทำการจองหรือรับผิดชอบค่าใช้จ่าย | 40, 223, … | ⚠️ missing 112,593 (~94%) → ตัดคอลัมน์ทิ้ง เหลือ flag `has_company` |

**คำย่อ**
- **TA** = Travel Agent (ตัวแทนท่องเที่ยว)
- **TO** = Tour Operator (ผู้ประกอบการนำเที่ยว)
- **GDS** = Global Distribution System (ระบบจองกลางที่เอเจนต์ใช้)

> ⭐ **ใช้อ้างอิงในหัวข้อ 4 ได้:** เปเปอร์ระบุว่าค่า NULL ใน `agent` และ `company` **"ไม่ควรถือเป็นค่าที่หายไป แต่หมายถึง 'ไม่เกี่ยวข้อง' (not applicable)"**
> คือการจองนั้นไม่ได้ทำผ่านเอเจนต์หรือบริษัท → เป็นเหตุผลโดยตรงว่าทำไมเราแปลงเป็น flag แทนการเติมค่าด้วย mean/mode

---

## 🛏️ 6. รายละเอียดการจอง

| คอลัมน์ | ชนิด | ความหมาย | ค่าที่พบ | การจัดการใน Notebook |
|---|---|---|---|---|
| `meal` | Categorical | แพ็กเกจอาหาร | `BB` = Bed & Breakfast, `HB` = Half Board (เช้า + อีก 1 มื้อ), `FB` = Full Board (3 มื้อ), `SC`/`Undefined` = ไม่มีอาหาร | รวม `Undefined` เข้ากับ `SC` |
| `reserved_room_type` | Categorical | ประเภทห้องที่**จอง**ไว้ (รหัสถูกปกปิด) | `A`, `B`, `C`, … | ใช้ |
| `assigned_room_type` | Categorical | ประเภทห้องที่**ได้จริง** (อาจต่างจากที่จอง เพราะเหตุผลด้านการจัดการของโรงแรมหรือลูกค้าขอเปลี่ยน) | `A`, `B`, `C`, … | ⚠️ ตัดทิ้ง (สงสัยว่าเป็น leakage — ดูส่วน 2.1 ของ Notebook) |
| `booking_changes` | Integer | จำนวนครั้งที่แก้ไขการจอง **นับตั้งแต่บันทึกการจองจนถึงเช็คอินหรือยกเลิก** | 0, 1, 2, … | ใช้ |
| `deposit_type` | Categorical | ประเภทเงินมัดจำ | `No Deposit` (ไม่มัดจำ), `Non Refund` (มัดจำเต็มจำนวน ไม่คืนเงิน), `Refundable` (มัดจำบางส่วน คืนได้) | ใช้ |
| `days_in_waiting_list` | Integer | จำนวนวันที่การจองอยู่ใน waiting list ก่อนได้รับการยืนยัน | 0, 1, … | ใช้ |
| `adr` | Numeric | **Average Daily Rate** = รายได้ค่าห้องทั้งหมด ÷ จำนวนคืนที่เข้าพัก | ทศนิยม (สกุลเงินยูโร) | ใช้ + ลบค่าติดลบและค่าเกิน 1,000 + สร้าง `adr_per_person` |
| `required_car_parking_spaces` | Integer | จำนวนที่จอดรถที่ลูกค้าขอ | 0, 1, 2, … | ใช้ |
| `total_of_special_requests` | Integer | จำนวนคำขอพิเศษ (เช่น เตียงคู่ ห้องชั้นสูง) | 0–5 | ใช้ |

---

## 🚫 7. ผลลัพธ์ของการจอง (ห้ามใช้ = Data Leakage)

| คอลัมน์ | ชนิด | ความหมาย | ค่าที่พบ | การจัดการใน Notebook |
|---|---|---|---|---|
| `reservation_status` | Categorical | สถานะสุดท้ายของการจอง | `Canceled` (ยกเลิก), `Check-Out` (เข้าพักแล้วออก), `No-Show` (ไม่มาและไม่แจ้ง) | ❌ ตัดทิ้ง |
| `reservation_status_date` | Date | วันที่ตั้งสถานะล่าสุด | `2015-07-01`, … | ❌ ตัดทิ้ง |

> ใน `is_canceled = 1` มีทั้งกรณี `Canceled` และ `No-Show` รวมกันอยู่
> → ควรเขียนไว้ในหัวข้อ 2 (Problem Definition) ว่า **"การยกเลิก" ในงานนี้รวมกรณีไม่มาเข้าพักโดยไม่แจ้งล่วงหน้าด้วย**

---

## ✨ Feature ที่สร้างเพิ่ม 9 ตัว (หัวข้อ 5.1)

| Feature ใหม่ | สร้างจาก | สมมติฐาน |
|---|---|---|
| `total_nights` | `stays_in_weekend_nights` + `stays_in_week_nights` | ทริปยาวต้องวางแผนมาก → โอกาสยกเลิกต่างจากทริปสั้น |
| `total_guests` | `adults` + `children` + `babies` | กลุ่มใหญ่ประสานงานยาก → โอกาสเปลี่ยนแผนสูงขึ้น |
| `is_family` | มี `children` หรือ `babies` | ครอบครัวมีแผนชัดเจนกว่า |
| `adr_per_person` | `adr` ÷ `total_guests` | ราคาต่อหัวสะท้อนความคุ้มค่าได้ดีกว่าราคาห้องรวม |
| `lead_time_group` | แบ่ง `lead_time` เป็นช่วง (0-7, 8-30, 31-90, 91-180, 181-365, 365+) | ความสัมพันธ์ระหว่างระยะจองล่วงหน้ากับการยกเลิกไม่เป็นเส้นตรง |
| `cancel_history_ratio` | `previous_cancellations` ÷ (เคยยกเลิก + เคยไม่ยกเลิก) | พฤติกรรมยกเลิกในอดีตบอกแนวโน้มในอนาคต |
| `season` | แปลง `arrival_date_month` เป็นฤดู | High season กับ Low season มีพฤติกรรมต่างกัน |
| `arrival_weekday` | วันในสัปดาห์ของวันที่เข้าพัก | เข้าพักวันธรรมดา (ธุรกิจ) vs วันหยุด (พักผ่อน) |
| `is_domestic` | `country == 'PRT'` | ลูกค้าในประเทศ (โปรตุเกส) ยกเลิกง่ายกว่าเพราะเดินทางสะดวก |

---

## 📌 ประเด็นที่ควรเขียนในรายงาน

1. **เปเปอร์ระบุว่าข้อมูลถูกดึงมา ณ วันก่อนวันเข้าพัก 1 วัน เพื่อป้องกันไม่ให้มีข้อมูลอนาคตปนเข้ามา** แต่ยังมีตัวแปรที่น่าสงสัย
   - `assigned_room_type` — Notebook ส่วน 2.1 ตรวจสอบด้วยข้อมูลจริงก่อนตัดสินใจตัด (ถ้าการจองที่ถูกเปลี่ยนห้องแทบไม่เคยถูกยกเลิก แปลว่ารู้ผลหลังเช็คอิน)
   - `booking_changes` — เปเปอร์บอกว่านับถึง "เช็คอิน**หรือยกเลิก**" จึงอาจมีข้อมูลหลังการจองติดมาบางส่วน ควรระบุเป็นข้อจำกัด
2. **ข้อมูลถูก anonymized แล้ว** ไม่มีชื่อหรือข้อมูลส่วนตัวของลูกค้า และรหัสห้อง `A`, `B`, `C` ถูกปกปิดความหมายไว้ → ไม่มีประเด็นด้านความเป็นส่วนตัว
3. **ตัวแปรที่เก็บเป็นตัวเลขแต่จริงๆ เป็น categorical:** `agent` และ `company` เป็นรหัส ID เอาไปคำนวณแบบตัวเลขไม่ได้ (agent หมายเลข 240 ไม่ได้ "มากกว่า" agent หมายเลข 9)
4. **เปเปอร์ระบุว่าฐานข้อมูล PMS รับประกันว่าไม่มีข้อมูลหายไป** ค่าที่เห็นเป็น missing บน Kaggle จึงเกิดจากการแปลงค่า NULL ที่แปลว่า "ไม่เกี่ยวข้อง" มาเป็นค่าว่างในไฟล์ CSV

---

## 📚 อ้างอิง

1. Antonio, N., de Almeida, A., & Nunes, L. (2019). *Hotel booking demand datasets*. **Data in Brief**, 22, 41–49. https://pmc.ncbi.nlm.nih.gov/articles/PMC6297060/
2. Hotel booking demand — Kaggle (jessemostipak). https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand
