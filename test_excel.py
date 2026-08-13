# import pandas as pd

# # ============================================================
# # STEP 1: Read the Ashley Furniture Excel file
# # ============================================================

# file_path = "ashley_198SKU (1).xlsx"

# df = pd.read_excel(file_path)

# # ============================================================
# # STEP 2: Show basic information
# # ============================================================

# print("\nExcel loaded successfully!")
# print("Number of rows:", len(df))
# print("Number of columns:", len(df.columns))

# # ============================================================
# # STEP 3: Show column names
# # ============================================================

# print("\nColumns:")
# for column in df.columns:
#     print("-", column)

# # ============================================================
# # STEP 4: Show first 10 SKUs
# # IMPORTANT: Excel column is "sku" in lowercase
# # ============================================================

# print("\nFirst 10 SKUs:")

# for sku in df["sku"].head(10):
#     print(sku)

# # ============================================================
# # STEP 5: Count missing SKU values
# # ============================================================

# print("\nMissing SKU values:", df["sku"].isna().sum())

# print("\nTest completed successfully!")

import pandas as pd
import requests


# ============================================================
# LOAD EXCEL
# ============================================================

file_path = r"C:\Users\SURAJ KS\projects\Ashley_Interview\ashley_198SKU (1).xlsx"

df = pd.read_excel(file_path)

print("Excel loaded successfully.")

print("Total SKUs:", len(df))


# ============================================================
# GET FIRST SKU
# ============================================================

sku = df["sku"].iloc[0]

landing_page = df["Landing page"].iloc[0]


print("\n========================================")
print("TEST PRODUCT")
print("========================================")

print("SKU:")
print(sku)

print("\nLanding page:")
print(landing_page)


# ============================================================
# SEND HTTP REQUEST
# ============================================================

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    )
}


print("\nSending request...")


try:

    response = requests.get(
        landing_page,
        headers=headers,
        timeout=20
    )


    print("\n========================================")
    print("RESPONSE")
    print("========================================")

    print("Status code:")
    print(response.status_code)

    print("\nFinal URL:")
    print(response.url)

    print("\nContent length:")
    print(len(response.text))


except Exception as e:

    print("\nRequest failed.")

    print(type(e).__name__)

    print(str(e))