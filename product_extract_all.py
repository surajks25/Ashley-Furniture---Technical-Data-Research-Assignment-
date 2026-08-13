import pandas as pd
import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException
)


# ============================================================
# CONFIGURATION
# ============================================================

EXCEL_FILE = r"C:\Users\SURAJ KS\projects\Ashley_Interview\ashley_198SKU (1).xlsx"

OUTPUT_FILE = r"C:\Users\SURAJ KS\projects\Ashley_Interview\ashley_product_results.xlsx"

# Chrome must already be running with:
#
# --remote-debugging-port=9222
#
# You manually open Ashley in this Chrome.
# You manually complete the human verification.
# Then this script attaches to that SAME Chrome.

CHROME_DEBUG_ADDRESS = "127.0.0.1:9222"

WAIT_TIME = 20

# ============================================================
# IMPORTANT TEST SETTING
# ============================================================
#
# True  = test only first SKU
# False = process all 198 SKUs
#
# FIRST RUN:
# Keep this TRUE.
#
# After A4000462 works successfully,
# change it to FALSE.
# ============================================================

TEST_ONLY_FIRST_SKU = True


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
# CHECK SKU COLUMN
# ============================================================

if "sku" not in df.columns:

    raise Exception(
        "ERROR: 'sku' column was not found in the Excel file."
    )


# ============================================================
# CLEAN SKU VALUES
# ============================================================

df = df.dropna(
    subset=["sku"]
).copy()

df["sku"] = (
    df["sku"]
    .astype(str)
    .str.strip()
)

print("Valid SKUs:", len(df))


# ============================================================
# CONNECT TO EXISTING CHROME
# ============================================================

print("\n========================================")
print("CONNECTING TO CHROME")
print("========================================")

options = webdriver.ChromeOptions()

options.add_experimental_option(
    "debuggerAddress",
    CHROME_DEBUG_ADDRESS
)


try:

    driver = webdriver.Chrome(
        options=options
    )

except Exception as e:

    print("\n========================================")
    print("CHROME CONNECTION FAILED")
    print("========================================")

    print("Error type:")
    print(type(e).__name__)

    print("\nError:")
    print(str(e))

    print("\nMake sure Chrome was started with:")
    print(
        '--remote-debugging-port=9222'
    )

    raise


wait = WebDriverWait(
    driver,
    WAIT_TIME
)


print("Selenium attached to Chrome.")

print("\nCurrent URL:")
print(driver.current_url)

print("\nPage title:")
print(driver.title)


# ============================================================
# RESULTS
# ============================================================

results = []


# ============================================================
# FUNCTION 1
# HANDLE ASHLEY POPUPS
# ============================================================

def handle_popups():

    print("\nChecking popups...")

    # ========================================================
    # STAY ON SITE
    # ========================================================

    try:

        stay_buttons = driver.find_elements(
            By.XPATH,
            "//*[normalize-space()='STAY ON SITE']"
        )

        for button in stay_buttons:

            try:

                if not button.is_displayed():

                    continue

                print(
                    "STAY ON SITE found."
                )

                try:

                    button.click()

                except Exception:

                    driver.execute_script(
                        "arguments[0].click();",
                        button
                    )

                print(
                    "STAY ON SITE clicked."
                )

                time.sleep(2)

                break

            except Exception:

                continue

    except Exception:

        pass


    # ========================================================
    # WAIT FOR BACKDROP
    # ========================================================

    try:

        WebDriverWait(
            driver,
            5
        ).until(
            EC.invisibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div.backdrop"
                )
            )
        )

    except Exception:

        pass


    # ========================================================
    # COOKIE BANNER
    # ========================================================

    try:

        cookie_buttons = driver.find_elements(
            By.XPATH,
            "//*[contains("
            "translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            "'accept all cookies'"
            ")]"
        )

        for button in cookie_buttons:

            try:

                if not button.is_displayed():

                    continue

                print(
                    "Accept All Cookies found."
                )

                try:

                    button.click()

                except Exception:

                    driver.execute_script(
                        "arguments[0].click();",
                        button
                    )

                print(
                    "Cookies accepted."
                )

                time.sleep(1)

                break

            except Exception:

                continue

    except Exception:

        pass


    # ========================================================
    # CLOSE VISIBLE NORMAL POPUPS
    # ========================================================

    try:

        close_buttons = driver.find_elements(
            By.XPATH,
            "//button[contains("
            "translate(@aria-label,"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            "'close'"
            ")]"
        )

        closed = 0

        for button in close_buttons:

            try:

                if not button.is_displayed():

                    continue

                try:

                    button.click()

                except Exception:

                    driver.execute_script(
                        "arguments[0].click();",
                        button
                    )

                closed += 1

                time.sleep(0.3)

            except Exception:

                continue

        if closed > 0:

            print(
                "Popup close buttons handled:",
                closed
            )

    except Exception:

        pass


# ============================================================
# FUNCTION 2
# CHECK HUMAN VERIFICATION / ACCESS DENIED
# ============================================================

def check_verification_page():

    try:

        current_url = driver.current_url

        title = driver.title.lower()

        body_text = ""

        try:

            body_text = driver.find_element(
                By.TAG_NAME,
                "body"
            ).text.lower()

        except Exception:

            pass


        # ====================================================
        # DETECT ACCESS DENIED
        # ====================================================

        if (
            "access to this page has been denied" in title
            or "access to this page has been denied" in body_text
        ):

            print("\n========================================")
            print("HUMAN VERIFICATION / ACCESS DENIED")
            print("========================================")

            print(
                "Ashley is showing the human-verification page."
            )

            print(
                "\nPlease complete the verification MANUALLY "
                "in the Chrome window."
            )

            print(
                "The script will wait for the normal Ashley "
                "page to return."
            )

            print(
                "\nWaiting up to 180 seconds..."
            )


            try:

                WebDriverWait(
                    driver,
                    180
                ).until(
                    lambda d:
                    (
                        "access to this page has been denied"
                        not in d.title.lower()
                    )
                )

                print(
                    "\nVerification page appears to be gone."
                )

                time.sleep(3)

                return True

            except TimeoutException:

                print(
                    "\nVerification did not complete "
                    "within 180 seconds."
                )

                return False


        return True

    except Exception:

        return True


# ============================================================
# FUNCTION 3
# FIND SEARCH BOX ON CURRENT PAGE
# ============================================================

def find_search_box():

    print(
        "\nLooking for search box..."
    )


    search_xpaths = [

        # Exact Ashley search input
        "//input[@placeholder='Search']",

        # Case-insensitive placeholder
        "//input[contains("
        "translate(@placeholder,"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'search'"
        ")]",

        # Search input by name
        "//input[@name='q']",

        # Search input by role
        "//input[@role='combobox']"

    ]


    last_error = None


    for xpath in search_xpaths:

        try:

            search_box = WebDriverWait(
                driver,
                5
            ).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        xpath
                    )
                )
            )


            if search_box.is_displayed():

                print(
                    "Search box found."
                )

                return search_box


        except Exception as e:

            last_error = e

            continue


    raise TimeoutException(
        "Ashley search box could not be found."
    )


# ============================================================
# FUNCTION 4
# SEARCH SKU
# ============================================================

def search_sku(sku):

    print("\n========================================")
    print("SEARCHING PRODUCT")
    print("========================================")

    print(
        "SKU:",
        sku
    )


    # ========================================================
    # CHECK HUMAN VERIFICATION
    # ========================================================

    if not check_verification_page():

        raise Exception(
            "Human verification did not complete."
        )


    # ========================================================
    # HANDLE POPUPS
    # ========================================================

    handle_popups()


    # ========================================================
    # FIND SEARCH BOX
    #
    # IMPORTANT:
    #
    # We DO NOT open Ashley home page here.
    #
    # The search box exists on:
    #
    # Home page
    # Search result page
    # Product page
    #
    # Therefore we can reuse the same browser session.
    # ========================================================

    search_box = find_search_box()


    # ========================================================
    # SCROLL TO SEARCH BOX
    # ========================================================

    try:

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            search_box
        )

        time.sleep(0.5)

    except Exception:

        pass


    # ========================================================
    # ENTER SKU
    # ========================================================

    try:

        search_box.click()

    except ElementClickInterceptedException:

        print(
            "Normal click intercepted."
        )

        driver.execute_script(
            "arguments[0].click();",
            search_box
        )


    search_box.clear()

    search_box.send_keys(
        sku
    )

    print(
        "SKU entered:",
        sku
    )


    # ========================================================
    # SUBMIT
    # ========================================================

    search_box.send_keys(
        Keys.ENTER
    )

    print(
        "Search submitted."
    )


    # ========================================================
    # WAIT FOR SEARCH RESULT
    # ========================================================

    print(
        "\nWaiting for search result..."
    )


    try:

        WebDriverWait(
            driver,
            WAIT_TIME
        ).until(
            lambda d:
            "/search-results" in d.current_url
        )

    except TimeoutException:

        # Sometimes Ashley updates the page slowly.
        time.sleep(5)

        if "/search-results" not in driver.current_url:

            raise


    time.sleep(4)


    print(
        "\nSearch result page loaded."
    )

    print(
        "Current URL:"
    )

    print(
        driver.current_url
    )


# ============================================================
# FUNCTION 5
# FIND PRODUCT URL
# ============================================================

def find_product_url(sku):

    print("\n========================================")
    print("FINDING PRODUCT URL")
    print("========================================")


    links = driver.find_elements(
        By.XPATH,
        "//a[@href]"
    )


    product_urls = []


    # ========================================================
    # FIND /p/ LINKS
    # ========================================================

    for link in links:

        try:

            href = link.get_attribute(
                "href"
            )

            if not href:

                continue


            if "/p/" not in href.lower():

                continue


            # Remove duplicate URLs

            if href not in product_urls:

                product_urls.append(
                    href
                )


        except (
            StaleElementReferenceException,
            Exception
        ):

            continue


    print(
        "Product URLs found:",
        len(product_urls)
    )


    # ========================================================
    # TRY TO MATCH SKU
    # ========================================================

    for url in product_urls:

        if sku.lower() in url.lower():

            print(
                "\nSKU matched in product URL."
            )

            print(
                "Product URL:"
            )

            print(
                url
            )

            return url


    # ========================================================
    # FALLBACK
    #
    # Search results normally contain the correct product
    # for an exact SKU search.
    # ========================================================

    if product_urls:

        print(
            "\nSKU was not found directly inside URL."
        )

        print(
            "Using first product URL."
        )

        print(
            product_urls[0]
        )

        return product_urls[0]


    # ========================================================
    # PRODUCT NOT FOUND
    # ========================================================

    print(
        "\nProduct URL NOT found."
    )

    return None


# ============================================================
# FUNCTION 6
# EXTRACT PRODUCT DATA
# ============================================================

def extract_product_data(
    sku,
    product_url
):

    print("\n========================================")
    print("OPENING PRODUCT PAGE")
    print("========================================")

    print(
        "Product URL:"
    )

    print(
        product_url
    )


    # ========================================================
    # OPEN PRODUCT
    # ========================================================

    driver.get(
        product_url
    )


    time.sleep(5)


    # ========================================================
    # CHECK VERIFICATION
    # ========================================================

    if not check_verification_page():

        raise Exception(
            "Human verification interrupted product page."
        )


    # ========================================================
    # HANDLE POPUPS
    # ========================================================

    handle_popups()


    time.sleep(2)


    # ========================================================
    # PRODUCT PAGE INFORMATION
    # ========================================================

    print("\n========================================")
    print("PRODUCT PAGE")
    print("========================================")

    print(
        "Current URL:"
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


    # ========================================================
    # PRODUCT NAME
    # ========================================================

    product_name = ""


    try:

        product_title = WebDriverWait(
            driver,
            WAIT_TIME
        ).until(
            EC.presence_of_element_located(
                (
                    By.TAG_NAME,
                    "h1"
                )
            )
        )


        product_name = (
            product_title
            .text
            .strip()
        )


    except Exception:

        product_name = ""


    # ========================================================
    # PAGE TEXT
    # ========================================================

    try:

        body_text = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text

    except Exception:

        body_text = ""


    # ========================================================
    # EXTRACT WEBSITE SKU
    # ========================================================

    extracted_sku = sku


    sku_match = re.search(
        r"Item:\s*([A-Za-z0-9]+)",
        body_text,
        re.IGNORECASE
    )


    if sku_match:

        extracted_sku = (
            sku_match
            .group(1)
            .strip()
        )


    # ========================================================
    # VALIDATE SKU
    # ========================================================

    sku_valid = (
        extracted_sku.lower()
        ==
        sku.lower()
    )


    print(
        "\nSKU validation:"
    )

    print(
        "Excel SKU:",
        sku
    )

    print(
        "Website SKU:",
        extracted_sku
    )

    print(
        "SKU Match:",
        sku_valid
    )


    # ========================================================
    # EXTRACT RATING
    # ========================================================

    rating = ""


    rating_patterns = [

        r"Rated\s+([0-9.]+)\s+out of\s+5",

        r"([0-9.]+)\s+out of\s+5"

    ]


    for pattern in rating_patterns:

        rating_match = re.search(
            pattern,
            body_text,
            re.IGNORECASE
        )

        if rating_match:

            rating = (
                rating_match
                .group(1)
            )

            break


    # ========================================================
    # EXTRACT PRICE
    # ========================================================

    price = ""


    if product_name:

        title_position = (
            body_text.find(
                product_name
            )
        )

        if title_position >= 0:

            product_section = (
                body_text[
                    title_position:
                    title_position + 3000
                ]
            )

        else:

            product_section = (
                body_text[:3000]
            )

    else:

        product_section = (
            body_text[:3000]
        )


    prices = re.findall(
        r"\$\s*[\d,]+\.\d{2}",
        product_section
    )


    if prices:

        price = prices[0]


    # ========================================================
    # EXTRACT DESCRIPTION
    # ========================================================

    description = ""


    # Pattern 1:
    #
    # Description
    # text
    # Made with

    description_match = re.search(
        r"Description\s*(.*?)\s*Made with",
        body_text,
        re.IGNORECASE | re.DOTALL
    )


    if description_match:

        description = (
            description_match
            .group(1)
            .strip()
        )


    else:

        # Pattern 2:
        #
        # Description
        # text
        # Dimensions

        description_match = re.search(
            r"Description\s*(.*?)\s*Dimensions",
            body_text,
            re.IGNORECASE | re.DOTALL
        )


        if description_match:

            description = (
                description_match
                .group(1)
                .strip()
            )


    # ========================================================
    # CLEAN DESCRIPTION
    # ========================================================

    description = re.sub(
        r"\s+",
        " ",
        description
    ).strip()


    # ========================================================
    # DISPLAY EXTRACTED DATA
    # ========================================================

    print("\n========================================")
    print("EXTRACTED PRODUCT")
    print("========================================")

    print(
        "SKU:",
        extracted_sku
    )

    print(
        "Product Name:",
        product_name
    )

    print(
        "Price:",
        price
    )

    print(
        "Rating:",
        rating
    )

    print(
        "Description:",
        description[:500]
    )

    print(
        "Product URL:",
        product_url
    )

    print(
        "SKU Valid:",
        sku_valid
    )


    # ========================================================
    # RETURN DATA
    # ========================================================

    return {

        "SKU":
            extracted_sku,

        "Product Name":
            product_name,

        "Price":
            price,

        "Rating":
            rating,

        "Description":
            description,

        "Product URL":
            product_url,

        "SKU Valid":
            sku_valid,

        "Status":
            "SUCCESS"
    }


# ============================================================
# FUNCTION 7
# SAVE RESULTS
# ============================================================

def save_results():

    try:

        output_df = pd.DataFrame(
            results
        )


        output_df.to_excel(
            OUTPUT_FILE,
            index=False
        )


        print(
            "\nProgress saved:"
        )

        print(
            OUTPUT_FILE
        )


    except Exception as e:

        print(
            "\nCould not save progress."
        )

        print(
            type(e).__name__
        )

        print(
            str(e)
        )


# ============================================================
# MAIN PROCESSING
# ============================================================

print("\n========================================")
print("STARTING PRODUCT EXTRACTION")
print("========================================")


# ============================================================
# SELECT SKUS
# ============================================================

if TEST_ONLY_FIRST_SKU:

    rows_to_process = df.head(1)

    print(
        "\nTEST MODE ENABLED"
    )

    print(
        "Only the first SKU will be processed."
    )

else:

    rows_to_process = df

    print(
        "\nFULL MODE ENABLED"
    )

    print(
        "All valid SKUs will be processed."
    )


# ============================================================
# PROCESS EACH SKU
# ============================================================

for index, row in rows_to_process.iterrows():

    sku = str(
        row["sku"]
    ).strip()


    print("\n\n")

    print(
        "########################################"
    )

    print(
        "PROCESSING SKU"
    )

    print(
        "########################################"
    )

    print(
        "Excel Row:",
        index + 1
    )

    print(
        "SKU:",
        sku
    )


    # ========================================================
    # SEARCH PRODUCT
    # ========================================================

    try:

        search_sku(
            sku
        )


    except Exception as e:

        print(
            "\n========================================"
        )

        print(
            "SEARCH FAILED"
        )

        print(
            "========================================"
        )

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )


        results.append({

            "SKU":
                sku,

            "Product Name":
                "",

            "Price":
                "",

            "Rating":
                "",

            "Description":
                "",

            "Product URL":
                "",

            "SKU Valid":
                False,

            "Status":
                "SEARCH_FAILED"
        })


        save_results()

        continue


    # ========================================================
    # FIND PRODUCT URL
    # ========================================================

    try:

        product_url = find_product_url(
            sku
        )


    except Exception as e:

        print(
            "\nProduct URL search failed."
        )

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        product_url = None


    # ========================================================
    # PRODUCT NOT FOUND
    # ========================================================

    if not product_url:

        print(
            "\nProduct not found."
        )

        results.append({

            "SKU":
                sku,

            "Product Name":
                "",

            "Price":
                "",

            "Rating":
                "",

            "Description":
                "",

            "Product URL":
                "",

            "SKU Valid":
                False,

            "Status":
                "PRODUCT_NOT_FOUND"
        })


        save_results()

        continue


    # ========================================================
    # EXTRACT PRODUCT
    # ========================================================

    try:

        product_data = (
            extract_product_data(
                sku,
                product_url
            )
        )


        results.append(
            product_data
        )


    except Exception as e:

        print(
            "\n========================================"
        )

        print(
            "PRODUCT EXTRACTION FAILED"
        )

        print(
            "========================================"
        )

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )


        results.append({

            "SKU":
                sku,

            "Product Name":
                "",

            "Price":
                "",

            "Rating":
                "",

            "Description":
                "",

            "Product URL":
                product_url,

            "SKU Valid":
                False,

            "Status":
                "EXTRACTION_FAILED"
        })


    # ========================================================
    # SAVE AFTER EVERY SKU
    # ========================================================

    save_results()


    # ========================================================
    # DELAY BEFORE NEXT SKU
    # ========================================================

    print(
        "\nWaiting before next SKU..."
    )

    time.sleep(3)


# ============================================================
# FINAL SAVE
# ============================================================

print("\n========================================")
print("FINAL SAVE")
print("========================================")

save_results()


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n========================================")
print("EXTRACTION COMPLETE")
print("========================================")


print(
    "Total processed:",
    len(results)
)


print(
    "Successful:",
    sum(
        1
        for r in results
        if r["Status"] == "SUCCESS"
    )
)


print(
    "Product not found:",
    sum(
        1
        for r in results
        if r["Status"] == "PRODUCT_NOT_FOUND"
    )
)


print(
    "Search failed:",
    sum(
        1
        for r in results
        if r["Status"] == "SEARCH_FAILED"
    )
)


print(
    "Extraction failed:",
    sum(
        1
        for r in results
        if r["Status"] == "EXTRACTION_FAILED"
    )
)


print(
    "\nOutput file:"
)

print(
    OUTPUT_FILE
)


# ============================================================
# IMPORTANT
#
# DO NOT USE driver.quit()
#
# Chrome was opened manually and Selenium is attached to it.
# Therefore we leave Chrome running.
# ============================================================

print(
    "\nKeeping Chrome open."
)

print(
    "Selenium test finished."
)