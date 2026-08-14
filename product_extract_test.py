import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ============================================================
# CONFIGURATION
# ============================================================

EXCEL_FILE = r"C:\Users\SURAJ KS\projects\Ashley_Interview\ashley_198SKU (1).xlsx"

TEST_ROW = 0

CHROME_DEBUG_ADDRESS = "127.0.0.1:9222"


# ============================================================
# LOAD EXCEL
# ============================================================

df = pd.read_excel(EXCEL_FILE)

sku = str(
    df["sku"].iloc[TEST_ROW]
).strip()

print("=" * 60)
print("TEST SKU")
print("=" * 60)

print("SKU:", sku)


# ============================================================
# CONNECT TO EXISTING CHROME
# ============================================================

options = webdriver.ChromeOptions()

options.add_experimental_option(
    "debuggerAddress",
    CHROME_DEBUG_ADDRESS
)

driver = webdriver.Chrome(
    options=options
)

print("\nConnected to Chrome.")

print("Current URL:")
print(driver.current_url)

print("Title:")
print(driver.title)


# ============================================================
# MAKE SURE WE ARE ON PRODUCT PAGE
# ============================================================

if "/p/" not in driver.current_url:

    print("\nYou are NOT on a product page.")
    print("Please open the Ashley product page manually.")

    raise SystemExit


# ============================================================
# FUNCTION TO CLICK TEXT
# ============================================================

def click_text(text):

    print(f"\nLooking for: {text}")

    elements = driver.find_elements(
        By.XPATH,
        f"//*[normalize-space()='{text}']"
    )

    for element in elements:

        try:

            if element.is_displayed():

                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    element
                )

                time.sleep(1)

                try:
                    element.click()

                except Exception:

                    driver.execute_script(
                        "arguments[0].click();",
                        element
                    )

                print(f"Clicked: {text}")

                time.sleep(2)

                return True

        except Exception:
            continue

    print(f"Could not click: {text}")

    return False


# ============================================================
# CLICK DETAILS & OVERVIEW
# ============================================================

click_text("Details & Overview")


# ============================================================
# CLICK DIMENSIONS
# ============================================================

click_text("Dimensions")


# ============================================================
# WAIT
# ============================================================

time.sleep(3)


# ============================================================
# GET FULL PAGE TEXT AGAIN
# ============================================================

print("\n" + "=" * 60)
print("PAGE TEXT AFTER CLICKING")
print("=" * 60)

body = driver.find_element(
    By.TAG_NAME,
    "body"
)

page_text = body.text

print(page_text)


# ============================================================
# IMAGE EXTRACTION TEST
# ============================================================

print("\n" + "=" * 60)
print("PRODUCT IMAGE TEST")
print("=" * 60)

images = driver.find_elements(
    By.TAG_NAME,
    "img"
)

print("Total IMG elements:", len(images))


image_urls = []


for img in images:

    try:

        src = img.get_attribute("src")

        data_src = img.get_attribute(
            "data-src"
        )

        srcset = img.get_attribute(
            "srcset"
        )

        alt = img.get_attribute(
            "alt"
        )

        url = src or data_src

        if url:

            if url not in image_urls:

                image_urls.append(url)

                print("\nImage:", len(image_urls))

                print("URL:")
                print(url)

                print("ALT:")
                print(alt)

                if srcset:

                    print("SRCSET:")
                    print(srcset)

    except Exception:
        continue


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("IMAGE SUMMARY")
print("=" * 60)

print(
    "Unique image URLs:",
    len(image_urls)
)


print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

print("\nKeep Chrome open.")

time.sleep(30)