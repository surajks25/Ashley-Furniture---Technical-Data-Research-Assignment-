import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time


# ============================================================
# CONFIGURATION
# ============================================================

EXCEL_FILE = r"C:\Users\SURAJ KS\projects\Ashley_Interview\ashley_198SKU (1).xlsx"

# Test only the first Excel row
TEST_ROW = 0


# ============================================================
# LOAD EXCEL
# ============================================================

print("\n========================================")
print("LOADING EXCEL")
print("========================================")

df = pd.read_excel(EXCEL_FILE)

print("Excel loaded successfully.")
print("Total SKUs:", len(df))


# ============================================================
# GET SKU
# ============================================================

sku = str(
    df["sku"].iloc[TEST_ROW]
).strip()

print("\n========================================")
print("TEST SKU")
print("========================================")

print("SKU:", sku)


# ============================================================
# CONNECT TO ALREADY OPEN CHROME
# ============================================================

print("\n========================================")
print("CONNECTING TO CHROME")
print("========================================")

options = webdriver.ChromeOptions()

options.add_experimental_option(
    "debuggerAddress",
    "127.0.0.1:9222"
)

driver = webdriver.Chrome(
    options=options
)

wait = WebDriverWait(
    driver,
    20
)

print("Selenium attached to Chrome.")

print("Current URL:")
print(driver.current_url)


try:

    # ========================================================
    # STEP 1: CHECK CURRENT PAGE
    # ========================================================

    current_url = driver.current_url

    print("\n========================================")
    print("CHECKING CURRENT PAGE")
    print("========================================")

    print(
        "Current URL:",
        current_url
    )


    # ========================================================
    # STEP 2:
    # IF ALREADY ON PRODUCT PAGE
    # USE IT DIRECTLY
    # ========================================================

    if "/p/" in current_url:

        print(
            "\nAlready on a product page."
        )

        print(
            "No search required."
        )

        product_url = current_url


    else:

        # ====================================================
        # STEP 3:
        # OPEN ASHLEY HOME PAGE
        # ====================================================

        print(
            "\nNot on a product page."
        )

        print(
            "Opening Ashley home page..."
        )

        driver.get(
            "https://www.ashleyfurniture.com/"
        )

        time.sleep(4)


        # ====================================================
        # STEP 4: HANDLE STAY ON SITE
        # ====================================================

        print(
            "\nChecking STAY ON SITE..."
        )

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

            print(
                "STAY ON SITE found."
            )

            try:

                stay_button.click()

            except Exception:

                driver.execute_script(
                    "arguments[0].click();",
                    stay_button
                )

            print(
                "STAY ON SITE clicked."
            )

            time.sleep(2)

        except Exception:

            print(
                "STAY ON SITE not found."
            )


        # ====================================================
        # STEP 5: HANDLE COOKIE BANNER
        # ====================================================

        print(
            "\nChecking cookie banner..."
        )

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

            print(
                "Cookies accepted."
            )

            time.sleep(2)

        except Exception:

            print(
                "Cookie banner not found."
            )


        # ====================================================
        # STEP 6: FIND SEARCH BOX
        # ====================================================

        print(
            "\nLooking for search box..."
        )

        search_box = WebDriverWait(
            driver,
            20
        ).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//input[@placeholder='Search']"
                )
            )
        )

        print(
            "Search box found."
        )


        # ====================================================
        # STEP 7: SEARCH SKU
        # ====================================================

        search_box.click()

        search_box.clear()

        search_box.send_keys(
            sku
        )

        print(
            "SKU entered:",
            sku
        )

        from selenium.webdriver.common.keys import Keys

        search_box.send_keys(
            Keys.ENTER
        )

        print(
            "Search submitted."
        )


        # ====================================================
        # STEP 8: WAIT SEARCH RESULT
        # ====================================================

        WebDriverWait(
            driver,
            20
        ).until(
            lambda d:
            "/search-results" in d.current_url
        )

        time.sleep(3)


        # ====================================================
        # STEP 9: FIND PRODUCT URL
        # ====================================================

        print(
            "\nLooking for product URL..."
        )

        links = driver.find_elements(
            By.XPATH,
            "//a[@href]"
        )

        product_urls = []


        for link in links:

            try:

                href = link.get_attribute(
                    "href"
                )

                if (
                    href
                    and "/p/" in href
                ):

                    if href not in product_urls:

                        product_urls.append(
                            href
                        )

            except Exception:

                continue


        print(
            "Product URLs found:",
            len(product_urls)
        )


        if not product_urls:

            raise Exception(
                "Product URL not found."
            )


        product_url = product_urls[0]

        print(
            "Product URL:",
            product_url
        )


        # ====================================================
        # STEP 10: OPEN PRODUCT PAGE
        # ====================================================

        driver.get(
            product_url
        )

        time.sleep(5)


    # ========================================================
    # STEP 11: PRODUCT PAGE
    # ========================================================

    print("\n========================================")
    print("PRODUCT PAGE")
    print("========================================")

    print(
        "URL:"
    )

    print(
        driver.current_url
    )

    print(
        "\nTitle:"
    )

    print(
        driver.title
    )


    # ========================================================
    # STEP 12: GET PRODUCT PAGE TEXT
    # ========================================================

    print("\n========================================")
    print("PRODUCT DATA")
    print("========================================")

    body = driver.find_element(
        By.TAG_NAME,
        "body"
    )

    page_text = body.text

    print(
        page_text[:8000]
    )


    # ========================================================
    # STEP 13: TEST COMPLETE
    # ========================================================

    print("\n========================================")
    print("TEST COMPLETE")
    print("========================================")

    print(
        "Keeping browser open for 30 seconds..."
    )

    time.sleep(30)


except Exception as e:

    print("\n========================================")
    print("ERROR")
    print("========================================")

    print(
        "Error:",
        type(e).__name__
    )

    print(
        str(e)
    )

    print(
        "\nCurrent URL:"
    )

    print(
        driver.current_url
    )

    print(
        "\nPage title:"
    )

    print(
        driver.title
    )

    time.sleep(20)


finally:

    # IMPORTANT:
    # Do NOT use driver.quit().
    # Chrome was opened manually and Selenium is attached to it.

    print(
        "\nSelenium test finished."
    )