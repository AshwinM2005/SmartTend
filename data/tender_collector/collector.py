from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)

from urllib.parse import urljoin
from datetime import datetime
import os
import json
import re

CPPP_URL = "https://eprocure.gov.in/eprocure/app"

BASE_FOLDER = "data/tenders"


def clean_text(text):
    if not text:
        return ""

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()

def safe_filename(text):

    text = clean_text(text)

    text = re.sub(
        r'[<>:"/\\|?*]',
        "",
        text
    )

    text = re.sub(
        r"\s+",
        "_",
        text
    )

    return text[:150]

def extract_field(text, pattern):

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:
        return clean_text(
            match.group(1)
        )

    return None

def extract_tender_data(page):

    # Get all visible webpage text
    page_text = page.locator(
        "body"
    ).inner_text()

    page_text = clean_text(
        page_text
    )

    # Extract fields

    tender_reference = extract_field(
        page_text,
        r"Tender Reference Number\s+(.+?)\s+Tender ID"
    )
    tender_id = extract_field(
        page_text,
        r"Tender ID\s+([A-Za-z0-9_\-]+)"
    )
    tender_type = extract_field(
        page_text,
        r"Tender Type\s+(.+?)\s+Form of contract"
    )
    tender_category = extract_field(
        page_text,
        r"Tender Category\s+(.+?)\s+No\. of Covers"
    )
    location = extract_field(
        page_text,
        r"Location\s+(.+?)\s+Pincode"
    )
    pincode = extract_field(
        page_text,
        r"Pincode\s+([0-9]+)"
    )
    bid_validity = extract_field(
        page_text,
        r"Bid Validity\(Days\)\s+([0-9]+)"
    )
    period_of_work = extract_field(
        page_text,
        r"Period Of Work\(Days\)\s+([0-9]+)"
    )
    tender_fee = extract_field(
        page_text,
        r"Tender Fee in ₹\s+([0-9,]+)"
    )
    emd_amount = extract_field(
        page_text,
        r"EMD Amount in ₹\s+([0-9,]+)"
    )
    publish_date = extract_field(
        page_text,
        r"Publish Date\s+(.+?)\s+Bid Opening Date"
    )
    bid_opening_date = extract_field(
        page_text,
        r"Bid Opening Date\s+(.+?)\s+Document Download"
    )
    document_download_start = extract_field(
        page_text,
        r"Document Download / Sale Start\s+Date\s+(.+?)\s+Document Download / Sale End"
    )
    document_download_end = extract_field(
        page_text,
        r"Document Download / Sale End\s+(.+?)\s+Clarification Start Date"
    )
    clarification_start = extract_field(
        page_text,
        r"Clarification Start Date\s+(.+?)\s+Clarification End Date"
    )
    clarification_end = extract_field(
        page_text,
        r"Clarification End Date\s+(.+?)\s+Bid Submission Start Date"
    )
    bid_submission_start = extract_field(
        page_text,
        r"Bid Submission Start Date\s+(.+?)\s+Bid Submission End Date"
    )
    bid_submission_end = extract_field(
        page_text,
        r"Bid Submission End Date\s+(.+?)\s+Tender Documents"
    )

    # Work / Item title

    work_title = extract_field(
        page_text,
        r"Work /Item\(s\)\s+Title\s+(.+?)\s+Work Description"
    )
    work_description = extract_field(
        page_text,
        r"Work Description\s+(.+?)\s+Pre Qualification"
    )

    organization = extract_field(
        page_text,
        r"Organisation Chain\s+(.+?)\s+Tender Reference"
    )

    authority_name = extract_field(
        page_text,
        r"Tender Inviting Authority\s+Name\s+(.+?)\s+Address"
    )


    # Build JSON object
    # --------------------------------------------------------

    tender_data = {

        "collection_timestamp":
            datetime.now().isoformat(),

        "source":
            "CPPP",

        "source_url":
            page.url,

        "tender_id":
            tender_id,

        "tender_reference":
            tender_reference,

        "organization":
            organization,

        "tender_type":
            tender_type,

        "tender_category":
            tender_category,

        "location":
            location,

        "pincode":
            pincode,

        "tender_fee":
            tender_fee,

        "emd_amount":
            emd_amount,

        "bid_validity_days":
            bid_validity,

        "period_of_work_days":
            period_of_work,

        "publish_date":
            publish_date,

        "document_download_start":
            document_download_start,

        "document_download_end":
            document_download_end,

        "clarification_start":
            clarification_start,

        "clarification_end":
            clarification_end,

        "bid_submission_start":
            bid_submission_start,

        "bid_submission_end":
            bid_submission_end,

        "bid_opening_date":
            bid_opening_date,

        "work_title":
            work_title,

        "work_description":
            work_description,

        "tender_inviting_authority":
            authority_name
    }

    return tender_data, page_text


# MAIN PROGRAM ///////////////////////////////////////////////////////////////
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context(
        accept_downloads=True
    )
    page = context.new_page()

# open cppp
    print ("hear")

    page.goto(
        CPPP_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )
    page.wait_for_timeout(
        3000
    )
# cpp opened 
# find tenders /////////////////////////////////////////////


    tender_links = page.locator(
        "a.link2"
    )

    tender_count = tender_links.count()
    print("\nTenders found:",tender_count)


    if tender_count == 0:
        print("No tenders found.")
        browser.close()
        exit()

    tenders_list = []
    for i in range(min(tender_count, 10)):
        title = clean_text(tender_links.nth(i).inner_text())
        href = clean_text(tender_links.nth(i).get_attribute("href"))

        if href:
            tenders_list.append({
                "title": title,
                "url": urljoin(CPPP_URL, href)
            })

    print(tenders_list)


    for i ,tender in enumerate(tenders_list, start=1):

        print("\n" + "=" * 60)
        print(f"PROCESSING TENDER {i}/{len(tenders_list)}")
        print("=" * 60)

        print("Title:", tender["title"])
        print("URL:", tender["url"])
        tender_url = tender["url"]
        tender_title = tender["title"]


        if not tenders_list:
            print("Tender URL not found.")
            browser.close()
            exit()

        
        print("\nSelected Tender:")
        print(tender_title)


        # ========================================================
        # 6. OPEN TENDER
        # ========================================================

        print("\nOpening tender page...")


        page.goto(
            tender_url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(
            5000
        )
        print("Tender page opened.")
        print(
            "URL:",
            page.url
        )


        # ========================================================
        # 7. EXTRACT WEBPAGE DATA
        # ========================================================

        print("\nExtracting tender webpage data...")


        tender_data, page_text = (
            extract_tender_data(page)
        )


        # ========================================================
        # 8. GET TENDER ID
        # ========================================================

        tender_id = tender_data.get(
            "tender_id"
        )


        if not tender_id:

            # Fallback if Tender ID extraction fails
            tender_id = (
                safe_filename(
                    tender_title
                )
            )


        print(
            "Tender ID:",
            tender_id
        )


        # ========================================================
        # 9. CREATE TENDER FOLDER
        # ========================================================

        tender_folder = os.path.join(
            BASE_FOLDER,
            safe_filename(
                tender_id
            )
        )


        os.makedirs(
            tender_folder,
            exist_ok=True
        )


        print("\nTender folder:")

        print(
            os.path.abspath(
                tender_folder
            )
        )


        # ========================================================
        # 10. SAVE JSON
        # ========================================================

        json_path = os.path.join(
            tender_folder,
            "tender_data.json"
        )


        with open(
            json_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                tender_data,
                f,
                indent=4,
                ensure_ascii=False
            )


        print(
            "Saved:",json_path)


        # ========================================================
        # 11. SAVE RAW HTML
        # ========================================================

        html_path = os.path.join(
            tender_folder,
            "tender_page.html"
        )


        html = page.content()


        with open(
            html_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                html
            )


        print(
            "Saved:",html_path)


        # ========================================================
        # 12. SAVE READABLE TEXT
        # ========================================================

        text_path = os.path.join(
            tender_folder,
            "tender_page.txt"
        )


        with open(
            text_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                page_text
            )


        print(
            "Saved:",text_path)


        # ========================================================
        # 13. FIND NIT DOCUMENT
        # ========================================================

        print("\nSearching for NIT document...")


        nit_link = page.locator(
            "a",
            has_text="Tendernotice_1.pdf"
        ).first


        try:

            nit_link.wait_for(
                state="visible",
                timeout=30000
            )


        except PlaywrightTimeoutError:

            print("Tendernotice_1.pdf not found.")

            browser.close()
            exit()


        print("NIT document found:")

        print(nit_link.inner_text().strip())


        # ========================================================
        # 14. FIRST CLICK
        #     NORMAL CPPP FLOW → CAPTCHA
        # ========================================================

        print("\nOpening CAPTCHA...")


        nit_link.click()


        page.wait_for_timeout(
            3000
        )


        print("\n""==================================================")
        print("CAPTCHA REQUIRED")
        print("==================================================")

        print("\nSolve the CAPTCHA in the browser.")


        try:

            nit_link_after_captcha = page.locator(
                "a",
                has_text="Tendernotice_1.pdf"
            ).first


            nit_link_after_captcha.wait_for(
                state="visible",
                timeout=300000
            )


            print("\nCAPTCHA completed.")

            print("Tender page detected.")


        except PlaywrightTimeoutError:

            print("\nCAPTCHA timeout.")

            browser.close()
            exit()


        page.wait_for_timeout(2000)


        # ========================================================
        # 17. FIND NIT AGAIN
        # ========================================================

        nit_link = page.locator(
            "a",
            has_text="Tendernotice_1.pdf"
        ).first


        if nit_link.count() == 0:

            print(
                "NIT link not found after CAPTCHA."
            )

            browser.close()
            exit()


        # ========================================================
        # 18. DOWNLOAD NIT
        # ========================================================

        nit_path = os.path.join(
            tender_folder,
            "main_tender.pdf"
        )


        print("\nDownloading NIT...")


        try:

            with page.expect_download(
                timeout=60000
            ) as download_info:

                nit_link.click()

            download = download_info.value

            # ----------------------------------------------------
            # Save as main_tender.pdf
            # ----------------------------------------------------

            download.save_as(
                nit_path
            )


            print("\nNIT downloaded successfully.")
            print(
                "Saved:",
                os.path.abspath(
                    nit_path
                )
            )


        except PlaywrightTimeoutError:

            print(
                "\nNIT download did not start."    )

            browser.close()
            exit()


        # ========================================================
        # 19. FINAL RESULT
        # ========================================================

        print("\n""==================================================")
        print("TENDER COLLECTION COMPLETE")
        print("==================================================")

        print("\nTender:")
        print(tender_title)

        print("\nTender ID:")
        print(tender_id)

        print("\nFiles:")
        print("1. tender_data.json")
        print("2. tender_page.html")
        print("3. tender_page.txt")
        print("4. main_tender.pdf")


        print("\nFolder:")
        print(
            os.path.abspath(
                tender_folder
            ))


    browser.close()