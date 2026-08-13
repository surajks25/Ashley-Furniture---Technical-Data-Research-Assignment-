from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# ============================================================
# TEST SKU
# ============================================================

sku = "R407681"


# ============================================================
# START CHROME
# ============================================================

driver = webdriver.Chrome()

wait = WebDriverWait(driver, 20)


try:

    # ========================================================
    # STEP 1: OPEN ASHLEY
    # ========================================================

    driver.get("https://www.ashleyfurniture.com/")

    print("\nAshley website opened.")

    time.sleep(4)


    # ========================================================
    # STEP 2: HANDLE "STAY ON SITE"
    # ========================================================

    print("Looking for STAY ON SITE button...")

    stay_elements = driver.find_elements(
        By.XPATH,
        "//*[normalize-space()='STAY ON SITE']"
    )

    clicked_stay = False

    for element in stay_elements:

        try:

            if element.is_displayed() and element.is_enabled():

                element.click()

                print("Clicked STAY ON SITE.")

                clicked_stay = True

                break

        except Exception:

            continue


    if clicked_stay:

        time.sleep(3)

        print("Location popup handled.")

    else:

        print("STAY ON SITE popup not found.")


    # ========================================================
    # STEP 3: CHECK FOR HUMAN VERIFICATION
    #
    # IMPORTANT:
    # We are NOT trying to bypass the verification.
    #
    # We only detect whether Ashley has presented it.
    # ========================================================

    print("\nChecking for human verification...")


    verification_found = False


    # Look for text shown on Ashley's verification page
    verification_text = driver.find_elements(
        By.XPATH,
        "//*[contains("
        "translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'before we continue'"
        ")]"
    )


    press_hold_text = driver.find_elements(
        By.XPATH,
        "//*[contains("
        "translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'press & hold'"
        ")]"
    )


    if verification_text or press_hold_text:

        verification_found = True


    # ========================================================
    # STEP 4: IF VERIFICATION IS FOUND
    # ========================================================

    if verification_found:

        print("\n========================================")
        print("HUMAN VERIFICATION DETECTED")
        print("========================================")

        print(
            "Ashley has presented a human-verification page."
        )

        print(
            "Selenium will NOT attempt to bypass it."
        )

        print(
            "If you want, complete the verification manually."
        )

        print(
            "The script will wait for the Ashley search box."
        )

        print(
            "\nWaiting up to 120 seconds..."
        )


        # ----------------------------------------------------
        # Wait for the search box to become available.
        #
        # If verification succeeds, Ashley should return
        # to a normal page containing the search box.
        # ----------------------------------------------------

        search_box = None

        end_time = time.time() + 120


        while time.time() < end_time:

            try:

                search_boxes = driver.find_elements(
                    By.XPATH,
                    "//input[contains("
                    "translate(@placeholder,"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                    "'abcdefghijklmnopqrstuvwxyz'),"
                    "'search'"
                    ")]"
                )


                for box in search_boxes:

                    if box.is_displayed() and box.is_enabled():

                        search_box = box

                        break


                if search_box is not None:

                    break


            except Exception:

                pass


            time.sleep(2)


        # ----------------------------------------------------
        # If search box was not found
        # ----------------------------------------------------

        if search_box is None:

            print("\n========================================")
            print("VERIFICATION DID NOT COMPLETE")
            print("========================================")

            print(
                "Ashley did not return to the normal page "
                "within 120 seconds."
            )

            print(
                "This means the automated browser cannot "
                "continue with this session."
            )

            print("\nCurrent URL:")

            print(driver.current_url)

            print("\nPage title:")

            print(driver.title)

            print(
                "\nKeeping browser open for inspection..."
            )

            time.sleep(30)

            # Stop this run cleanly.
            # No Selenium exception is generated.

            raise SystemExit


        print(
            "\nVerification page is no longer blocking "
            "the search."
        )


    else:

        # ====================================================
        # STEP 5: NO VERIFICATION DETECTED
        # ====================================================

        print(
            "Human verification was not detected."
        )


        # ----------------------------------------------------
        # Find search box normally
        # ----------------------------------------------------

        search_box = wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//input[contains("
                    "translate(@placeholder,"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                    "'abcdefghijklmnopqrstuvwxyz'),"
                    "'search'"
                    ")]"
                )
            )
        )


    # ========================================================
    # STEP 6: SEARCH BOX FOUND
    # ========================================================

    print("Search box found.")


    # ========================================================
    # STEP 7: ENTER SKU
    # ========================================================

    search_box.click()

    search_box.clear()

    search_box.send_keys(sku)

    print(
        "SKU entered:",
        sku
    )


    # ========================================================
    # STEP 8: SUBMIT SEARCH
    # ========================================================

    search_box.send_keys(Keys.ENTER)

    print("Search submitted.")


    # ========================================================
    # STEP 9: WAIT FOR SEARCH RESULTS
    # ========================================================

    print(
        "Waiting for search results..."
    )

    time.sleep(6)


    # ========================================================
    # STEP 10: DISPLAY SEARCH RESULT INFORMATION
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
    # STEP 11: FIND PRODUCT LINKS
    # ========================================================

    print(
        "\nLooking for product links..."
    )


    links = driver.find_elements(
        By.XPATH,
        "//a[@href]"
    )


    print(
        "Total links found:",
        len(links)
    )


    # ========================================================
    # STEP 12: FIND LINKS CONTAINING /p/
    #
    # Ashley product URLs contain /p/
    # ========================================================

    product_links = []

    for link in links:

        try:

            href = link.get_attribute("href")

            text = link.text.strip()


            if href and "/p/" in href:

                # Avoid duplicate URLs
                if href not in product_links:

                    product_links.append(href)

                    print(
                        "\nProduct link",
                        len(product_links)
                    )

                    print(
                        "Text:",
                        text[:100]
                    )

                    print(
                        "URL:",
                        href
                    )


        except Exception:

            continue


    # ========================================================
    # STEP 13: PRODUCT LINK SUMMARY
    # ========================================================

    print(
        "\n========================================"
    )

    print(
        "PRODUCT LINK SUMMARY"
    )

    print(
        "========================================"
    )

    print(
        "Total possible product links:",
        len(product_links)
    )


    # ========================================================
    # STEP 14: SHOW FIRST PRODUCT URL
    # ========================================================

    if product_links:

        print(
            "\nFirst product URL:"
        )

        print(
            product_links[0]
        )

    else:

        print(
            "\nNo product URL was found."
        )


    # ========================================================
    # STEP 15: KEEP BROWSER OPEN
    #
    # Useful for visual inspection while developing.
    # ========================================================

    print(
        "\nKeeping browser open for 20 seconds..."
    )

    time.sleep(20)


# ============================================================
# ERROR HANDLING
# ============================================================

except SystemExit:

    # --------------------------------------------------------
    # Expected exit when verification blocks automation.
    # --------------------------------------------------------

    pass


except Exception as e:

    # --------------------------------------------------------
    # Display the actual error instead of hiding it.
    # --------------------------------------------------------

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
    # STEP 16: CLOSE BROWSER
    # ========================================================

    driver.quit()

    print(
        "\nBrowser closed."
    )