import os
import pymupdf

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

RAW_DATA_DIR = os.path.join(
    BASE_DIR,
    "tender_collector",
    "data",
    "tenders"
)

print(RAW_DATA_DIR)

tender_folders = [
    folder
    for folder in os.listdir(RAW_DATA_DIR)
    if os.path.isdir(os.path.join(RAW_DATA_DIR, folder))
]


tender_id = tender_folders[1]
tender_path = os.path.join(
    RAW_DATA_DIR,
    tender_id
)
print(tender_id)

# /////////////////////////////////////PDF path

pdf_path =  os.path.join(
    tender_path,
    "main_tender.pdf"
)

if os.path.exists(pdf_path):
    print("PDF found")

    document = pymupdf.open(pdf_path)
    pdf_text = ""

    for page in document:
        pdf_text += page.get_text()

    document.close()

    print(pdf_text[:2000])

else:
    print("PDF not found")