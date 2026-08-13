import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException

import time


# ============================================================
# CONFIGURATION
# ============================================================

EXCEL_FILE = r"C:\Users\SURAJ KS\projects\Ashley_Interview\ashley_198SKU (1).xlsx"

# Test only ONE SKU first
TEST_ROW = 0


# ============================================================
# STEP 1: LOAD EXCEL
# ============================================================

print("\n========================================")
print("LOADING EXCEL")
print("========================================")

df = pd.read_excel(EXCEL_FILE)

print("Excel loaded successfully.")
print("Total SKUs:", len(df))


# ============================================================
# STEP 2: GET SKU FROM EXCEL
# ============================================================

sku = str(df["sku"].iloc[TEST_ROW]).strip()

print("\n========================================")
print("TEST SKU")
print("========================================")

print("SKU:", sku)


# ============================================================
# STEP 3: CONNECT TO ALREADY OPEN CHROME
#
# IMPORTANT:
# Chrome must already be running with:
#
# --remote-debugging-port=9222
#
# ============================================================

print("\n========================================")
print("CONNECTING TO CHROME")
print("========================================")

options = webdriver.ChromeOptions()

options.add_experimental_option(
    "debuggerAddress",
    "127.0.0.1:9222"
)

driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, 20)

print("Selenium attached to Chrome.")

print("Current URL:")
print(driver.current_url)


try:

    # ========================================================
    # STEP 4: HANDLE LOCATION POPUP
    # ========================================================

    print("\n========================================")
    print("CHECKING LOCATION POPUP")
    print("========================================")

    try:

        stay_button = WebDriverWait(
            driver,
            5
        ).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//*[normalize-space()='STAY ON SITE']"
                )
            )
        )

        print("STAY ON SITE found.")

        try:

            stay_button.click()

            print("STAY ON SITE clicked.")

        except Exception:

            driver.execute_script(
                "arguments[0].click();",
                stay_button
            )

            print("STAY ON SITE clicked using JavaScript.")

        time.sleep(2)

    except TimeoutException:

        print("STAY ON SITE popup not found.")


    # ========================================================
    # STEP 5: HANDLE COOKIE BANNER
    # ========================================================

    print("\n========================================")
    print("CHECKING COOKIE BANNER")
    print("========================================")

    try:

        cookie_button = WebDriverWait(
            driver,
            3
        ).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//*[normalize-space()='Accept All Cookies']"
                )
            )
        )

        cookie_button.click()

        print("Cookies accepted.")

        time.sleep(2)

    except TimeoutException:

        print("Cookie banner not found.")

    except Exception as e:

        print(
            "Cookie banner could not be clicked:",
            type(e).__name__
        )


    # ========================================================
    # STEP 6: CLOSE VISIBLE CLOSE BUTTONS
    # ========================================================

    print("\n========================================")
    print("CHECKING CLOSE BUTTONS")
    print("========================================")

    close_buttons = driver.find_elements(
        By.XPATH,
        "//button[contains("
        "translate(@aria-label,"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'close'"
        ")]"
    )

    print(
        "Close buttons found:",
        len(close_buttons)
    )

    for button in close_buttons:

        try:

            if button.is_displayed():

                button.click()

                print("Closed visible close button.")

                time.sleep(0.5)

        except Exception:

            continue


    # ========================================================
    # STEP 7: FIND SEARCH BOX
    # ========================================================

    print("\n========================================")
    print("LOOKING FOR SEARCH BOX")
    print("========================================")

    search_box = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//input[@placeholder='Search']"
            )
        )
    )

    print("Search box found.")


    # ========================================================
    # STEP 8: SEARCH SKU
    # ========================================================

    search_box.click()

    search_box.clear()

    search_box.send_keys(sku)

    print("SKU entered:", sku)

    search_box.send_keys(Keys.ENTER)

    print("Search submitted.")


    # ========================================================
    # STEP 9: WAIT FOR SEARCH RESULT
    # ========================================================

    print("\nWaiting for search result...")

    WebDriverWait(
        driver,
        20
    ).until(
        lambda d:
        "/search-results" in d.current_url
    )

    time.sleep(3)

    print("\nSearch result page loaded.")

    print("Current URL:")
    print(driver.current_url)


    # ========================================================
    # STEP 10: FIND PRODUCT URL
    # ========================================================

    print("\n========================================")
    print("FINDING PRODUCT URL")
    print("========================================")

    links = driver.find_elements(
        By.XPATH,
        "//a[@href]"
    )

    product_urls = []

    for link in links:

        try:

            href = link.get_attribute("href")

            if href and "/p/" in href:

                if href not in product_urls:

                    product_urls.append(href)

        except Exception:

            continue


    print(
        "Product URLs found:",
        len(product_urls)
    )


    # ========================================================
    # STEP 11: CHECK PRODUCT URL
    # ========================================================

    if not product_urls:

        print("\nERROR: Product URL was not found.")

        raise SystemExit


    product_url = product_urls[0]

    print("\nProduct URL:")
    print(product_url)


    # ========================================================
    # STEP 12: OPEN PRODUCT PAGE
    # ========================================================

    print("\n========================================")
    print("OPENING PRODUCT PAGE")
    print("========================================")

    driver.get(product_url)

    print("Product page requested.")

    time.sleep(5)


    # ========================================================
    # STEP 13: PRINT PRODUCT PAGE INFORMATION
    # ========================================================

    print("\n========================================")
    print("PRODUCT PAGE")
    print("========================================")

    print("Current URL:")
    print(driver.current_url)

    print("\nPage title:")
    print(driver.title)


    # ========================================================
    # STEP 14: PRINT PAGE TEXT
    #
    # This is ONLY for inspection.
    #
    # We will use the actual HTML structure in the next step
    # instead of guessing field selectors.
    # ========================================================

    print("\n========================================")
    print("PAGE TEXT SAMPLE")
    print("========================================")

    body_text = driver.find_element(
        By.TAG_NAME,
        "body"
    ).text

    print(body_text[:5000])


    # ========================================================
    # STEP 15: KEEP BROWSER OPEN
    # ========================================================

    print("\n========================================")
    print("TEST COMPLETE")
    print("========================================")

    print(
        "Keeping Chrome open for 30 seconds..."
    )

    time.sleep(30)


except Exception as e:

    print("\n========================================")
    print("ERROR")
    print("========================================")

    print(
        "Error type:",
        type(e).__name__
    )

    print(
        "Error:",
        str(e)
    )

    print("\nCurrent URL:")
    print(driver.current_url)

    print("\nPage title:")
    print(driver.title)

    time.sleep(20)


finally:

    # ========================================================
    # IMPORTANT:
    # DO NOT driver.quit()
    #
    # Selenium is attached to your manually opened Chrome.
    # We want your Chrome to remain open.
    # ========================================================

    print("\nSelenium test finished.")