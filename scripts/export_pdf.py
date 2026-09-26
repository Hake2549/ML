"""แปลงไฟล์ .pptx เป็น .pdf ด้วย Microsoft PowerPoint ที่ติดตั้งในเครื่อง (Windows เท่านั้น)

วิธีรัน (จาก root ของ repo):  python scripts/export_pdf.py
"""
from pathlib import Path
import win32com.client

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'slides' / 'Hotel-Booking-Cancellation-Prediction.pptx'
DST = SRC.with_suffix('.pdf')

app = win32com.client.Dispatch('PowerPoint.Application')
deck = app.Presentations.Open(str(SRC), WithWindow=False)
try:
    deck.SaveAs(str(DST), 32)   # 32 = ppSaveAsPDF
finally:
    deck.Close()
    app.Quit()
print(f'saved: {DST} ({DST.stat().st_size/1e6:.2f} MB)')
