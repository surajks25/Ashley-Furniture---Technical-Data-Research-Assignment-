from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


# ============================================================
# TEST SKU
# ============================================================

sku = "R407681"


# ============================================================
# CONNECT TO ALREADY-OPEN CHROME
# ============================================================

options = webdriver.ChromeOptions()

options.add_experimental_option(
    "debuggerAddress",
    "127.0.0.1:9222"
)


driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, 20)


try:

    print("\n========================================")
    print("SELENIUM ATTACHED TO CHROME")
    print("========================================")

    print("Current URL:")
    print(driver.current_url)

    print("\nPage title:")
    print(driver.title)


    # ========================================================
    # STEP 1: HANDLE STAY ON SITE POPUP
    # ========================================================

    print("\n========================================")
    print("CHECKING LOCATION POPUP")
    print("========================================")

    stay_clicked = False

    try:

        print("Looking for STAY ON SITE...")

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

        # Scroll it into view
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            stay_button
        )

        time.sleep(1)

        try:

            stay_button.click()

            print("STAY ON SITE clicked normally.")

            stay_clicked = True

        except Exception:

            print(
                "Normal click failed. "
                "Trying JavaScript click..."
            )

            driver.execute_script(
                "arguments[0].click();",
                stay_button
            )

            print(
                "STAY ON SITE clicked using JavaScript."
            )

            stay_clicked = True


    except TimeoutException:

        print(
            "STAY ON SITE popup not found."
        )


    # ========================================================
    # STEP 2: WAIT FOR LOCATION POPUP/BACKDROP TO DISAPPEAR
    # ========================================================

    if stay_clicked:

        print(
            "\nWaiting for location popup to disappear..."
        )

        try:

            WebDriverWait(
                driver,
                10
            ).until(
                EC.invisibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div.backdrop"
                    )
                )
            )

            print(
                "Location popup/backdrop disappeared."
            )

        except TimeoutException:

            print(
                "Backdrop did not disappear "
                "within 10 seconds."
            )


    # ========================================================
    # STEP 3: HANDLE COOKIE BANNER
    # ========================================================

    print("\n========================================")
    print("CHECKING COOKIE BANNER")
    print("========================================")

    try:

        accept_cookie = WebDriverWait(
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

        print("Accept All Cookies found.")

        accept_cookie.click()

        print("Cookies accepted.")

        time.sleep(2)

    except TimeoutException:

        print(
            "Cookie banner not found."
        )

    except Exception:

        print(
            "Cookie banner was found "
            "but could not be clicked."
        )


    # ========================================================
    # STEP 4: CLOSE OTHER VISIBLE CLOSE BUTTONS
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

                print(
                    "Closed visible close button."
                )

                time.sleep(1)

        except Exception:

            continue


    # ========================================================
    # STEP 5: FIND SEARCH BOX
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

    print("Search box found and clickable.")


    # ========================================================
    # STEP 6: ENTER SKU
    # ========================================================

    search_box.click()

    search_box.clear()

    search_box.send_keys(sku)

    print(
        "SKU entered:",
        sku
    )


    # ========================================================
    # STEP 7: SUBMIT SEARCH
    # ========================================================

    search_box.send_keys(Keys.ENTER)

    print(
        "Search submitted."
    )


    # ========================================================
    # STEP 8: WAIT FOR SEARCH RESULTS
    # ========================================================

    print(
        "\nWaiting for search results..."
    )

    time.sleep(6)


    # ========================================================
    # STEP 9: DISPLAY RESULT PAGE
    # ========================================================

    print("\n========================================")
    print("SEARCH RESULT")
    print("========================================")

    print(
        "SKU:",
        sku
    )

    print(
        "Current URL:"
    )

    print(
        driver.current_url
    )

    print(
        "Page title:"
    )

    print(
        driver.title
    )


    # ========================================================
    # STEP 10: FIND PRODUCT LINKS
    # ========================================================

    print("\n========================================")
    print("LOOKING FOR PRODUCT LINKS")
    print("========================================")

    links = driver.find_elements(
        By.XPATH,
        "//a[@href]"
    )

    print(
        "Total links found:",
        len(links)
    )


    product_links = []


    for link in links:

        try:

            href = link.get_attribute(
                "href"
            )

            text = link.text.strip()


            if href and "/p/" in href:

                if href not in product_links:

                    product_links.append(
                        href
                    )

                    print(
                        "\nProduct:",
                        text[:100]
                    )

                    print(
                        "URL:",
                        href
                    )


        except Exception:

            continue


    # ========================================================
    # STEP 11: FINAL RESULT
    # ========================================================

    print("\n========================================")
    print("FINAL RESULT")
    print("========================================")

    print(
        "Total product links:",
        len(product_links)
    )


    if product_links:

        print(
            "\nSUCCESS!"
        )

        print(
            "First product URL:"
        )

        print(
            product_links[0]
        )

    else:

        print(
            "\nNo product URL found."
        )


    # ========================================================
    # STEP 12: KEEP BROWSER OPEN
    # ========================================================

    print(
        "\nKeeping browser open for 20 seconds..."
    )

    time.sleep(20)


except Exception as e:

    print("\n========================================")
    print("ERROR")
    print("========================================")

    print(
        type(e).__name__
    )

    print(
        str(e)
    )


finally:

    # ========================================================
    # IMPORTANT
    #
    # Because Selenium is attached to an existing Chrome,
    # we don't want to close your manually opened browser.
    # ========================================================

    print(
        "\nSelenium test finished."
    )