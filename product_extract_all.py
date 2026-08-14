import os
import re
import json
import html
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = r"C:\Users\SURAJ KS\projects\Ashley_Interview\ashley_198SKU (1).xlsx"

OUTPUT_FILE = r"C:\Users\SURAJ KS\projects\Ashley_Interview\ashley_product_results.xlsx"

CHROME_DEBUG_ADDRESS = "127.0.0.1:9222"

WAIT_TIME = 30

# ============================================================
# FULL MODE
# ============================================================
# False = process all SKUs
#
# DO NOT CHANGE THIS TO TRUE.
# ============================================================

TEST_ONLY_FIRST_SKU = False


# ============================================================
# EXCEL COLUMNS
# ============================================================

OUTPUT_COLUMNS = [
    "sku",
    "Landing page",
    "imageSet",
    "Description",
    "Color",
    "Price",
    "Series Name",
    "UPC",
    "cartonDepthInches",
    "cartonHeightInches",
    "cartonVolumeCuFeet",
    "cartonWidthInches",
    "chairQtyPerCarton",
    "unitDepthInches",
    "unitFriendlyDimensionsInches",
    "unitHeightInches",
    "unitWidthInches"
]


# ============================================================
# LOAD INPUT EXCEL
# ============================================================

print("\n")
print("=" * 60)
print("ASHLEY PRODUCT DATA EXTRACTOR")
print("=" * 60)

print("\n")
print("=" * 60)
print("LOADING INPUT EXCEL")
print("=" * 60)

try:
    input_df = pd.read_excel(INPUT_FILE)

except Exception as e:

    print("\nCould not load input Excel.")

    print(e)

    raise


print(
    "Input Excel loaded successfully."
)

print(
    "Total rows:",
    len(input_df)
)

print(
    "Columns:",
    list(input_df.columns)
)


# ============================================================
# CHECK SKU COLUMN
# ============================================================

if "sku" not in input_df.columns:

    raise Exception(
        "ERROR: 'sku' column was not found."
    )


# ============================================================
# CLEAN INPUT DATA
# ============================================================

input_df["sku"] = (
    input_df["sku"]
    .astype(str)
    .str.strip()
)

input_df = input_df[
    ~input_df["sku"].isin(
        [
            "",
            "nan",
            "None"
        ]
    )
].copy()


# ============================================================
# LOAD EXISTING OUTPUT IF AVAILABLE
# ============================================================
#
# This is important.
#
# If the script already processed some SKUs and then stopped,
# we keep those results.
#
# When the script runs again, it can continue.
# ============================================================

if os.path.exists(OUTPUT_FILE):

    print("\n")
    print("=" * 60)
    print("EXISTING OUTPUT FOUND")
    print("=" * 60)

    try:

        df = pd.read_excel(
            OUTPUT_FILE
        )

        print(
            "Existing output loaded."
        )

        print(
            "Existing rows:",
            len(df)
        )

    except Exception:

        print(
            "Existing output could not be loaded."
        )

        print(
            "Creating output from input."
        )

        df = input_df.copy()

else:

    print("\n")
    print(
        "No existing output found."
    )

    print(
        "Creating output from input Excel."
    )

    df = input_df.copy()


# ============================================================
# MAKE SURE ALL REQUIRED COLUMNS EXIST
# ============================================================

for column in OUTPUT_COLUMNS:

    if column not in df.columns:

        df[column] = ""


# ============================================================
# KEEP ONLY INPUT SKUS / PRESERVE INPUT ORDER
# ============================================================

# Create a lookup of existing extracted results.

existing_data = {}

for _, row in df.iterrows():

    sku_value = str(
        row.get(
            "sku",
            ""
        )
    ).strip()

    if sku_value:

        existing_data[
            sku_value
        ] = row.to_dict()


# ============================================================
# REBUILD OUTPUT BASED ON ORIGINAL INPUT
# ============================================================

new_rows = []

for _, input_row in input_df.iterrows():

    sku = str(
        input_row["sku"]
    ).strip()

    # Start with original input row
    row_data = input_row.to_dict()

    # If previous extraction exists, preserve it
    if sku in existing_data:

        old_data = existing_data[sku]

        for column in OUTPUT_COLUMNS:

            old_value = old_data.get(
                column,
                ""
            )

            # Preserve previously extracted non-empty value
            if (
                old_value is not None
                and
                str(old_value).strip()
                not in [
                    "",
                    "nan",
                    "None"
                ]
            ):

                row_data[column] = old_value

    new_rows.append(
        row_data
    )


df = pd.DataFrame(
    new_rows
)


# ============================================================
# FORCE OUTPUT COLUMNS TO OBJECT
# ============================================================
#
# Fixes:
#
# TypeError:
# Invalid value '249.99'
# for dtype 'float64'
#
# ============================================================

for column in OUTPUT_COLUMNS:

    df[column] = (
        df[column]
        .astype(object)
    )


print(
    "\nFinal working rows:",
    len(df)
)


# ============================================================
# CONNECT TO CHROME
# ============================================================

print("\n")
print("=" * 60)
print("CONNECTING TO CHROME")
print("=" * 60)

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

    print("\n")
    print("=" * 60)
    print("CHROME CONNECTION FAILED")
    print("=" * 60)

    print(e)

    print(
        "\nMake sure Chrome is running with:"
    )

    print(
        '--remote-debugging-port=9222'
    )

    raise


print(
    "Selenium attached to Chrome."
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


# ============================================================
# POPUP HANDLER
# ============================================================

def handle_popups():

    print(
        "\nChecking popups..."
    )

    # --------------------------------------------------------
    # ACCEPT ALL COOKIES
    # --------------------------------------------------------

    try:

        elements = driver.find_elements(
            By.XPATH,
            "//*[contains("
            "translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            "'accept all cookies'"
            ")]"
        )

        for element in elements:

            try:

                if not element.is_displayed():

                    continue

                print(
                    "Accept All Cookies found."
                )

                try:

                    element.click()

                except Exception:

                    driver.execute_script(
                        "arguments[0].click();",
                        element
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


    # --------------------------------------------------------
    # STAY ON SITE
    # --------------------------------------------------------

    try:

        elements = driver.find_elements(
            By.XPATH,
            "//*[normalize-space()='STAY ON SITE']"
        )

        for element in elements:

            try:

                if not element.is_displayed():

                    continue

                try:

                    element.click()

                except Exception:

                    driver.execute_script(
                        "arguments[0].click();",
                        element
                    )

                print(
                    "STAY ON SITE clicked."
                )

                time.sleep(1)

                break

            except Exception:

                continue

    except Exception:

        pass


# ============================================================
# HUMAN VERIFICATION
# ============================================================
#
# IMPORTANT:
# We do NOT try to bypass verification.
#
# If Ashley asks for human verification:
#
# 1. Complete it manually.
# 2. Come back to terminal.
# 3. Press ENTER.
#
# ============================================================

def handle_human_verification():

    try:

        body_text = ""

        try:

            body_text = driver.find_element(
                By.TAG_NAME,
                "body"
            ).text.lower()

        except Exception:

            pass


        title = driver.title.lower()


        verification_words = [
            "before we continue",
            "press & hold",
            "press and hold",
            "confirm you are a human",
            "and not a bot"
        ]


        verification_found = False


        for word in verification_words:

            if word in body_text:

                verification_found = True

                break


            if word in title:

                verification_found = True

                break


        if not verification_found:

            return True


        # ----------------------------------------------------
        # MANUAL VERIFICATION
        # ----------------------------------------------------

        print("\n")
        print("=" * 60)
        print("HUMAN VERIFICATION DETECTED")
        print("=" * 60)

        print()

        print(
            "Ashley requires manual human verification."
        )

        print()

        print(
            "1. Go to the Chrome window."
        )

        print(
            "2. Complete the 'Press & Hold' verification."
        )

        print(
            "3. Wait until the Ashley page opens."
        )

        print(
            "4. Return to this terminal."
        )

        print(
            "5. Press ENTER."
        )

        print()

        print("=" * 60)


        input(
            "\nPress ENTER after completing verification..."
        )


        print(
            "\nContinuing..."
        )


        time.sleep(3)

        return True


    except Exception as e:

        print(
            "\nVerification handling error:"
        )

        print(e)

        return False


# ============================================================
# DIRECT SEARCH
# ============================================================

def search_sku(sku):

    print("\n")
    print("=" * 40)
    print("SEARCHING PRODUCT")
    print("=" * 40)

    print(
        "SKU:",
        sku
    )


    # --------------------------------------------------------
    # DIRECT SEARCH URL
    # --------------------------------------------------------

    search_url = (
        "https://www.ashleyfurniture.com/"
        "search-results?q="
        + sku
    )


    print(
        "\nOpening direct search URL:"
    )

    print(
        search_url
    )


    try:

        driver.get(
            search_url
        )

    except Exception as e:

        print(
            "Could not open search URL."
        )

        print(e)

        return False


    time.sleep(5)


    # --------------------------------------------------------
    # HUMAN VERIFICATION
    # --------------------------------------------------------

    if not handle_human_verification():

        return False


    # --------------------------------------------------------
    # POPUPS
    # --------------------------------------------------------

    handle_popups()


    # --------------------------------------------------------
    # WAIT FOR SEARCH RESULTS
    # --------------------------------------------------------

    print(
        "\nWaiting for search results..."
    )


    try:

        WebDriverWait(
            driver,
            WAIT_TIME
        ).until(
            lambda d:
            (
                "/search-results"
                in d.current_url
            )
        )

    except TimeoutException:

        print(
            "\nSearch result page timeout."
        )

        print(
            "Current URL:",
            driver.current_url
        )

        return False


    time.sleep(2)


    # --------------------------------------------------------
    # HUMAN VERIFICATION AGAIN
    # --------------------------------------------------------

    # We only check once more.
    # If it appears, user can complete it.

    if not handle_human_verification():

        return False


    print(
        "\nSearch result page loaded."
    )

    print(
        "Current URL:",
        driver.current_url
    )


    return True


# ============================================================
# FIND PRODUCT URL
# ============================================================

def find_product_url(sku):

    print("\n")
    print("=" * 40)
    print("FINDING PRODUCT URL")
    print("=" * 40)


    product_urls = []


    try:

        links = driver.find_elements(
            By.XPATH,
            "//a[@href]"
        )


        for link in links:

            try:

                href = link.get_attribute(
                    "href"
                )


                if not href:

                    continue


                if "/p/" not in href.lower():

                    continue


                if href not in product_urls:

                    product_urls.append(
                        href
                    )


            except Exception:

                continue


    except Exception as e:

        print(
            "Could not find product links."
        )

        print(e)

        return None


    print(
        "Product URLs found:",
        len(product_urls)
    )


    # --------------------------------------------------------
    # EXACT SKU MATCH
    # --------------------------------------------------------

    sku_lower = sku.lower()


    for url in product_urls:

        if sku_lower in url.lower():

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


    print(
        "\nNo matching product URL found."
    )

    return None


# ============================================================
# JSON-LD PRODUCT
# ============================================================

def get_product_json():

    try:

        scripts = driver.find_elements(
            By.XPATH,
            "//script[@type='application/ld+json']"
        )


        for script in scripts:

            try:

                raw = script.get_attribute(
                    "innerHTML"
                )


                if not raw:

                    continue


                raw = html.unescape(
                    raw
                ).strip()


                data = json.loads(
                    raw
                )


                # ------------------------------------------------
                # DICT
                # ------------------------------------------------

                if isinstance(
                    data,
                    dict
                ):

                    data_type = data.get(
                        "@type"
                    )


                    if data_type == "Product":

                        return data


                    # @graph

                    graph = data.get(
                        "@graph"
                    )


                    if isinstance(
                        graph,
                        list
                    ):

                        for item in graph:

                            if not isinstance(
                                item,
                                dict
                            ):

                                continue


                            if (
                                item.get("@type")
                                == "Product"
                            ):

                                return item


                # ------------------------------------------------
                # LIST
                # ------------------------------------------------

                if isinstance(
                    data,
                    list
                ):

                    for item in data:

                        if not isinstance(
                            item,
                            dict
                        ):

                            continue


                        if (
                            item.get("@type")
                            == "Product"
                        ):

                            return item


            except Exception:

                continue


    except Exception:

        pass


    return {}


# ============================================================
# GET SERIES NAME
# ============================================================

def get_series_name():

    try:

        element = driver.find_element(
            By.XPATH,
            "//input[@name='series_Name']"
        )


        value = element.get_attribute(
            "value"
        )


        if value:

            return value.strip()


    except Exception:

        pass


    # Source fallback

    try:

        source = driver.page_source


        patterns = [

            r'"series_Name"\s*:\s*"([^"]+)"',

            r'&quot;series_Name&quot;\s*:\s*&quot;([^&]+)&quot;'

        ]


        for pattern in patterns:

            match = re.search(
                pattern,
                source,
                re.IGNORECASE
            )


            if match:

                return html.unescape(
                    match.group(1)
                ).strip()


    except Exception:

        pass


    return ""


# ============================================================
# GET UPC
# ============================================================

def get_upc():

    source = driver.page_source


    patterns = [

        r'"upc"\s*:\s*"([0-9]+)"',

        r'&quot;upc&quot;\s*:\s*&quot;([0-9]+)&quot;',

        r'\\"upc\\"\s*:\s*\\"([0-9]+)'

    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            source,
            re.IGNORECASE
        )


        if match:

            return match.group(1)


    return ""


# ============================================================
# GET COLOR
# ============================================================

def get_color(
    product_json,
    body
):

    color = product_json.get(
        "color",
        ""
    )


    if color:

        return str(
            color
        ).strip()


    # Visible page fallback

    lines = [
        line.strip()
        for line in body.splitlines()
        if line.strip()
    ]


    for i, line in enumerate(lines):

        if line.lower() == "color":

            if i + 1 < len(lines):

                value = lines[
                    i + 1
                ].strip()


                if value:

                    return value


        if line.lower().startswith(
            "color:"
        ):

            value = line.split(
                ":",
                1
            )[1].strip()


            if value:

                return value


    return ""


# ============================================================
# GET PRICE
# ============================================================

def get_price(
    product_json,
    body
):

    offers = product_json.get(
        "offers",
        {}
    )


    if isinstance(
        offers,
        dict
    ):

        price = offers.get(
            "price"
        )


        if price is not None:

            try:

                return float(
                    price
                )

            except Exception:

                return str(
                    price
                )


    # Visible page fallback

    matches = re.findall(
        r"\$\s*([\d,]+\.\d{2})",
        body
    )


    if matches:

        try:

            return float(
                matches[0].replace(
                    ",",
                    ""
                )
            )

        except Exception:

            pass


    return ""


# ============================================================
# GET DESCRIPTION
# ============================================================

def get_description(
    product_json
):

    description = product_json.get(
        "description",
        ""
    )


    if description:

        return re.sub(
            r"\s+",
            " ",
            str(description)
        ).strip()


    return ""


# ============================================================
# GET IMAGES
# ============================================================

def get_images(
    product_json
):

    images = product_json.get(
        "image",
        []
    )


    if isinstance(
        images,
        str
    ):

        images = [
            images
        ]


    clean_images = []


    for image in images:

        if not image:

            continue


        image = str(
            image
        ).strip()


        if image not in clean_images:

            clean_images.append(
                image
            )


    return " | ".join(
        clean_images
    )


# ============================================================
# CLICK DIMENSIONS
# ============================================================

def click_dimensions():

    print(
        "\nLooking for Dimensions..."
    )


    try:

        elements = driver.find_elements(
            By.XPATH,
            "//*[normalize-space()='Dimensions']"
        )


        for element in elements:

            try:

                if not element.is_displayed():

                    continue


                driver.execute_script(
                    """
                    arguments[0].scrollIntoView({
                        block: 'center'
                    });
                    """,
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


                print(
                    "Dimensions clicked."
                )


                time.sleep(2)


                return True


            except Exception:

                continue


    except Exception:

        pass


    print(
        "Dimensions section not found."
    )

    return False


# ============================================================
# DIMENSION VALUE
# ============================================================

def get_dimension_value(
    body,
    label
):

    lines = [
        line.strip()
        for line in body.splitlines()
        if line.strip()
    ]


    # --------------------------------------------------------
    # Exact line format
    # --------------------------------------------------------

    for i, line in enumerate(lines):

        clean = (
            line
            .lower()
            .strip()
            .rstrip(":")
        )


        if clean == label.lower():

            if i + 1 < len(lines):

                value = lines[
                    i + 1
                ].strip()


                if re.search(
                    r"\d",
                    value
                ):

                    return value


    # --------------------------------------------------------
    # Same line format
    #
    # Width: 20.75"
    # --------------------------------------------------------

    pattern = (
        re.escape(label)
        +
        r"\s*:?\s*"
        r"([0-9]+(?:\.[0-9]+)?\s*(?:\"|″|in|inches)?)"
    )


    match = re.search(
        pattern,
        body,
        re.IGNORECASE
    )


    if match:

        return match.group(1).strip()


    return ""


# ============================================================
# GET DIMENSIONS
# ============================================================

def get_dimensions():

    click_dimensions()


    time.sleep(2)


    try:

        body = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text

    except Exception:

        return (
            "",
            "",
            "",
            ""
        )


    unit_width = get_dimension_value(
        body,
        "Width"
    )


    unit_height = get_dimension_value(
        body,
        "Height"
    )


    unit_depth = get_dimension_value(
        body,
        "Depth"
    )


    # --------------------------------------------------------
    # FRIENDLY DIMENSIONS
    # --------------------------------------------------------

    friendly = ""


    # Try Ashley style
    # 21"W x 21"D x 25"H

    patterns = [

        r"\d+(?:\.\d+)?\s*[\"″]\s*W\s*x\s*"
        r"\d+(?:\.\d+)?\s*[\"″]\s*D\s*x\s*"
        r"\d+(?:\.\d+)?\s*[\"″]\s*H",

        r"\d+(?:\.\d+)?\s*W\s*x\s*"
        r"\d+(?:\.\d+)?\s*D\s*x\s*"
        r"\d+(?:\.\d+)?\s*H"

    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            body,
            re.IGNORECASE
        )


        if match:

            friendly = (
                match.group(0)
                .strip()
            )

            break


    # If friendly dimensions are not shown,
    # create them from the extracted dimensions.

    if (
        not friendly
        and
        unit_width
        and
        unit_depth
        and
        unit_height
    ):

        friendly = (
            f"{unit_width} W x "
            f"{unit_depth} D x "
            f"{unit_height} H"
        )


    print(
        "Unit Depth:",
        unit_depth
    )

    print(
        "Friendly Dimensions:",
        friendly
    )

    print(
        "Unit Height:",
        unit_height
    )

    print(
        "Unit Width:",
        unit_width
    )


    return (
        unit_depth,
        friendly,
        unit_height,
        unit_width
    )


# ============================================================
# CARTON / OTHER DETAILS
# ============================================================

def get_carton_data(
    body
):

    carton_depth = ""
    carton_height = ""
    carton_volume = ""
    carton_width = ""
    chair_qty = ""


    # --------------------------------------------------------
    # Carton Depth
    # --------------------------------------------------------

    match = re.search(
        r"Carton\s+Depth\s*:?\s*"
        r"([0-9]+(?:\.[0-9]+)?)",
        body,
        re.IGNORECASE
    )


    if match:

        carton_depth = match.group(1)


    # --------------------------------------------------------
    # Carton Height
    # --------------------------------------------------------

    match = re.search(
        r"Carton\s+Height\s*:?\s*"
        r"([0-9]+(?:\.[0-9]+)?)",
        body,
        re.IGNORECASE
    )


    if match:

        carton_height = match.group(1)


    # --------------------------------------------------------
    # Carton Volume
    # --------------------------------------------------------

    match = re.search(
        r"Carton\s+Volume"
        r"(?:\s*\(.*?\))?"
        r"\s*:?\s*"
        r"([0-9]+(?:\.[0-9]+)?)",
        body,
        re.IGNORECASE
    )


    if match:

        carton_volume = match.group(1)


    # --------------------------------------------------------
    # Carton Width
    # --------------------------------------------------------

    match = re.search(
        r"Carton\s+Width\s*:?\s*"
        r"([0-9]+(?:\.[0-9]+)?)",
        body,
        re.IGNORECASE
    )


    if match:

        carton_width = match.group(1)


    # --------------------------------------------------------
    # Chair quantity
    # --------------------------------------------------------

    patterns = [

        r"Chair\s+Quantity\s+Per\s+Carton\s*:?\s*"
        r"([0-9]+)",

        r"Chair\s+Qty\s+Per\s+Carton\s*:?\s*"
        r"([0-9]+)",

        r"Quantity\s+Per\s+Carton\s*:?\s*"
        r"([0-9]+)"

    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            body,
            re.IGNORECASE
        )


        if match:

            chair_qty = match.group(1)

            break


    return (
        carton_depth,
        carton_height,
        carton_volume,
        carton_width,
        chair_qty
    )


# ============================================================
# EXTRACT PRODUCT
# ============================================================

def extract_product(
    sku,
    product_url
):

    print("\n")
    print("=" * 60)
    print("OPENING PRODUCT PAGE")
    print("=" * 60)

    print(
        "Product URL:"
    )

    print(
        product_url
    )


    # --------------------------------------------------------
    # OPEN PRODUCT
    # --------------------------------------------------------

    driver.get(
        product_url
    )


    time.sleep(5)


    # --------------------------------------------------------
    # HUMAN VERIFICATION
    # --------------------------------------------------------

    if not handle_human_verification():

        raise Exception(
            "Human verification was not completed."
        )


    handle_popups()


    print("\n")
    print("=" * 60)
    print("PRODUCT PAGE")
    print("=" * 60)

    print(
        "Current URL:",
        driver.current_url
    )

    print(
        "Page title:",
        driver.title
    )


    # --------------------------------------------------------
    # BODY
    # --------------------------------------------------------

    body = driver.find_element(
        By.TAG_NAME,
        "body"
    ).text


    source = driver.page_source


    # --------------------------------------------------------
    # JSON-LD
    # --------------------------------------------------------

    product_json = get_product_json()


    # ========================================================
    # WEBSITE SKU
    # ========================================================

    website_sku = ""


    match = re.search(
        r"Item:\s*([A-Za-z0-9_-]+)",
        body,
        re.IGNORECASE
    )


    if match:

        website_sku = (
            match.group(1)
            .strip()
        )


    if not website_sku:

        website_sku = str(
            product_json.get(
                "sku",
                ""
            )
        ).strip()


    if not website_sku:

        website_sku = sku


    sku_valid = (
        website_sku.lower()
        ==
        sku.lower()
    )


    print("\n")
    print("SKU VALIDATION")

    print(
        "Excel SKU:",
        sku
    )

    print(
        "Website SKU:",
        website_sku
    )

    print(
        "SKU Match:",
        sku_valid
    )


    # ========================================================
    # PRODUCT NAME
    # ========================================================

    product_name = ""


    try:

        h1_elements = driver.find_elements(
            By.TAG_NAME,
            "h1"
        )


        for element in h1_elements:

            try:

                if element.is_displayed():

                    product_name = (
                        element.text
                        .strip()
                    )

                    if product_name:

                        break

            except Exception:

                continue


    except Exception:

        pass


    if not product_name:

        product_name = str(
            product_json.get(
                "name",
                ""
            )
        ).strip()


    # ========================================================
    # LANDING PAGE
    # ========================================================

    landing_page = (
        driver.current_url
    )


    # ========================================================
    # IMAGE SET
    # ========================================================

    image_set = get_images(
        product_json
    )


    # ========================================================
    # DESCRIPTION
    # ========================================================

    description = get_description(
        product_json
    )


    # ========================================================
    # COLOR
    # ========================================================

    color = get_color(
        product_json,
        body
    )


    # ========================================================
    # PRICE
    # ========================================================

    price = get_price(
        product_json,
        body
    )


    # ========================================================
    # SERIES
    # ========================================================

    series_name = get_series_name()


    # ========================================================
    # UPC
    # ========================================================

    upc = get_upc()


    # ========================================================
    # DIMENSIONS
    # ========================================================

    (
        unit_depth,
        friendly_dimensions,
        unit_height,
        unit_width
    ) = get_dimensions()


    # ========================================================
    # CARTON DATA
    # ========================================================

    (
        carton_depth,
        carton_height,
        carton_volume,
        carton_width,
        chair_qty
    ) = get_carton_data(
        body
    )


    # ========================================================
    # FINAL DATA
    # ========================================================

    product_data = {

        "sku":
            sku,

        "Landing page":
            landing_page,

        "imageSet":
            image_set,

        "Description":
            description,

        "Color":
            color,

        "Price":
            price,

        "Series Name":
            series_name,

        "UPC":
            upc,

        "cartonDepthInches":
            carton_depth,

        "cartonHeightInches":
            carton_height,

        "cartonVolumeCuFeet":
            carton_volume,

        "cartonWidthInches":
            carton_width,

        "chairQtyPerCarton":
            chair_qty,

        "unitDepthInches":
            unit_depth,

        "unitFriendlyDimensionsInches":
            friendly_dimensions,

        "unitHeightInches":
            unit_height,

        "unitWidthInches":
            unit_width
    }


    # ========================================================
    # PRINT RESULT
    # ========================================================

    print("\n")
    print("=" * 60)
    print("EXTRACTED PRODUCT")
    print("=" * 60)


    for column in OUTPUT_COLUMNS:

        print(
            f"{column}: "
            f"{product_data.get(column, '')}"
        )


    return product_data


# ============================================================
# SAVE EXCEL
# ============================================================

def save_excel():

    print("\n")
    print(
        "Saving Excel..."
    )


    try:

        # Force object dtype
        for column in OUTPUT_COLUMNS:

            df[column] = (
                df[column]
                .astype(object)
            )


        # Keep exact required columns first
        existing_columns = [
            column
            for column in df.columns
            if column not in OUTPUT_COLUMNS
        ]


        final_columns = (
            OUTPUT_COLUMNS
            +
            existing_columns
        )


        df.to_excel(
            OUTPUT_FILE,
            index=False,
            columns=final_columns
        )


        print(
            "Excel saved successfully:"
        )

        print(
            OUTPUT_FILE
        )

        return True


    except PermissionError:

        print("\n")
        print("=" * 60)
        print("EXCEL FILE IS OPEN")
        print("=" * 60)

        print(
            "Please close:"
        )

        print(
            OUTPUT_FILE
        )

        print(
            "Then press ENTER in the terminal."
        )


        input()


        try:

            df.to_excel(
                OUTPUT_FILE,
                index=False,
                columns=final_columns
            )

            print(
                "Excel saved successfully."
            )

            return True

        except Exception as e:

            print(
                "Could not save Excel:"
            )

            print(e)

            return False


    except Exception as e:

        print(
            "Excel save error:"
        )

        print(e)

        return False


# ============================================================
# UPDATE ONE ROW
# ============================================================

def update_excel_row(
    index,
    product_data
):

    print("\n")
    print(
        "Writing extracted data into Excel..."
    )


    # --------------------------------------------------------
    # Convert columns to object
    # --------------------------------------------------------

    for column in OUTPUT_COLUMNS:

        df[column] = (
            df[column]
            .astype(object)
        )


    # --------------------------------------------------------
    # WRITE VALUES
    # --------------------------------------------------------

    for column in OUTPUT_COLUMNS:

        value = product_data.get(
            column,
            ""
        )


        if value is None:

            value = ""


        df.at[
            index,
            column
        ] = value


    # --------------------------------------------------------
    # SAVE IMMEDIATELY
    # --------------------------------------------------------

    saved = save_excel()


    if saved:

        print(
            "\nDATA SUCCESSFULLY WRITTEN TO EXCEL."
        )


    return saved


# ============================================================
# DETERMINE ROWS TO PROCESS - RESUME MODE
# ============================================================
#
# IMPORTANT:
# The script checks the existing output Excel before processing.
#
# If "Landing page" already contains a value:
#     -> SKU is considered completed
#     -> SKU is SKIPPED
#
# If "Landing page" is empty:
#     -> SKU is considered incomplete
#     -> SKU is processed
#
# This means you can safely stop the script because of human
# verification and run it again later. Previously completed SKUs
# will NOT be fetched again.
# ============================================================

def is_completed_row(row):
    """
    Decide whether a SKU has already been successfully extracted.

    Landing page is used as the main completion marker because
    it is written only when product extraction succeeds.
    """

    landing_page = row.get("Landing page", "")

    if landing_page is None:
        return False

    value = str(landing_page).strip()

    return value not in ["", "nan", "None"]


if TEST_ONLY_FIRST_SKU:

    # --------------------------------------------------------
    # TEST MODE
    # --------------------------------------------------------
    # Process only the first incomplete SKU.
    # --------------------------------------------------------

    incomplete_rows = df[
        ~df.apply(is_completed_row, axis=1)
    ]

    rows_to_process = incomplete_rows.head(1)

    print("\n")
    print("=" * 60)
    print("TEST MODE - RESUME")
    print("=" * 60)

    print(
        "Only the first incomplete SKU will be processed."
    )

else:

    # --------------------------------------------------------
    # FULL RESUME MODE
    # --------------------------------------------------------
    # Process ONLY rows that do not already have a Landing page.
    # --------------------------------------------------------

    completed_mask = df.apply(
        is_completed_row,
        axis=1
    )

    rows_to_process = df[
        ~completed_mask
    ]

    completed_count = int(
        completed_mask.sum()
    )

    remaining_count = len(
        rows_to_process
    )

    print("\n")
    print("=" * 60)
    print("RESUME EXTRACTION MODE")
    print("=" * 60)

    print(
        "Total SKUs:",
        len(df)
    )

    print(
        "Already completed:",
        completed_count
    )

    print(
        "Remaining SKUs:",
        remaining_count
    )

    if remaining_count > 0:

        print(
            "Starting from SKU:",
            str(
                rows_to_process.iloc[0]["sku"]
            ).strip()
        )

    else:

        print(
            "ALL SKUs ARE ALREADY COMPLETED."
        )


# ============================================================
# COUNTERS
# ============================================================

successful = 0

search_failed = 0

product_not_found = 0

extraction_failed = 0


# ============================================================
# PROCESS ALL SKUS
# ============================================================

for position, (index, row) in enumerate(
    rows_to_process.iterrows(),
    start=1
):


    sku = str(
        row["sku"]
    ).strip()


    print("\n\n")
    print("#" * 60)
    print(
        f"PROCESSING {position} / "
        f"{len(rows_to_process)}"
    )
    print("#" * 60)

    print(
        "Excel Row:",
        index + 2
    )

    print(
        "SKU:",
        sku
    )

    # ========================================================
    # SAFETY CHECK - SKIP ALREADY COMPLETED ROWS
    # ========================================================
    #
    # This is a second protection layer. Even if a completed row
    # somehow enters rows_to_process, do not search Ashley again.
    # ========================================================

    if is_completed_row(df.loc[index]):

        print(
            "\nSKIPPING SKU - DATA ALREADY EXISTS:"
        )

        print(
            sku
        )

        continue


    # ========================================================
    # SEARCH
    # ========================================================

    search_success = search_sku(
        sku
    )


    if not search_success:

        search_failed += 1

        print(
            "\nSEARCH FAILED:"
        )

        print(
            sku
        )

        # ----------------------------------------------------
        # Continue to next SKU
        # ----------------------------------------------------

        continue


    # ========================================================
    # FIND PRODUCT
    # ========================================================

    product_url = find_product_url(
        sku
    )


    if not product_url:

        product_not_found += 1

        print(
            "\nPRODUCT NOT FOUND:"
        )

        print(
            sku
        )

        continue


    # ========================================================
    # EXTRACT PRODUCT
    # ========================================================

    try:

        product_data = extract_product(
            sku,
            product_url
        )


        # ----------------------------------------------------
        # VALIDATE SKU
        # ----------------------------------------------------

        if not product_data:

            raise Exception(
                "No product data returned."
            )


        if (
            str(
                product_data["sku"]
            ).lower()
            !=
            sku.lower()
        ):

            raise Exception(
                "SKU validation failed."
            )


        # ----------------------------------------------------
        # WRITE TO EXCEL
        # ----------------------------------------------------

        saved = update_excel_row(
            index,
            product_data
        )


        if saved:

            successful += 1


    except Exception as e:

        extraction_failed += 1


        print("\n")
        print(
            "=" * 60
        )

        print(
            "PRODUCT EXTRACTION FAILED"
        )

        print(
            "=" * 60
        )

        print(
            "SKU:",
            sku
        )

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )


    # ========================================================
    # WAIT
    # ========================================================

    print("\n")
    print(
        "Waiting before next SKU..."
    )

    time.sleep(3)


# ============================================================
# FINAL SAVE
# ============================================================

print("\n")
print("=" * 60)
print("FINAL SAVE")
print("=" * 60)

save_excel()


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 60)
print("EXTRACTION COMPLETE")
print("=" * 60)

print(
    "Total processed:",
    len(rows_to_process)
)

print(
    "Successful:",
    successful
)

print(
    "Product not found:",
    product_not_found
)

print(
    "Search failed:",
    search_failed
)

print(
    "Extraction failed:",
    extraction_failed
)

print("\n")
print(
    "Output file:"
)

print(
    OUTPUT_FILE
)

print("\n")
print(
    "Chrome will remain open."
)

print(
    "Selenium finished."
)