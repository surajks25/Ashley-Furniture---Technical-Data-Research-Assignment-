import pandas as pd
import re
import json

from selenium import webdriver
from selenium.webdriver.common.by import By


# ============================================================
# CONNECT TO EXISTING CHROME
# ============================================================

options = webdriver.ChromeOptions()

options.add_experimental_option(
    "debuggerAddress",
    "127.0.0.1:9222"
)

driver = webdriver.Chrome(options=options)

print("=" * 60)
print("CONNECTED")
print("=" * 60)

print("URL:")
print(driver.current_url)

print("TITLE:")
print(driver.title)


# ============================================================
# GET HTML
# ============================================================

html = driver.page_source

print("\nHTML LENGTH:")
print(len(html))


# ============================================================
# SEARCH FOR IMPORTANT FIELD NAMES
# ============================================================

keywords = [
    "upc",
    "UPC",
    "carton",
    "Carton",
    "series",
    "Series",
    "chair quantity",
    "quantity per carton",
    "package",
    "dimensions"
]


print("\n" + "=" * 60)
print("SEARCHING PAGE SOURCE")
print("=" * 60)


for keyword in keywords:

    count = html.lower().count(
        keyword.lower()
    )

    print(
        f"{keyword}: {count} occurrences"
    )


# ============================================================
# PRINT CONTEXT AROUND KEYWORDS
# ============================================================

def print_context(keyword, max_results=5):

    print("\n" + "-" * 60)
    print("KEYWORD:", keyword)
    print("-" * 60)

    pattern = re.compile(
        re.escape(keyword),
        re.IGNORECASE
    )

    matches = list(
        pattern.finditer(html)
    )

    print(
        "Matches:",
        len(matches)
    )

    for match in matches[:max_results]:

        start = max(
            0,
            match.start() - 500
        )

        end = min(
            len(html),
            match.end() + 1000
        )

        text = html[start:end]

        print("\n--- MATCH ---")
        print(text)


# ============================================================
# CHECK IMPORTANT FIELDS
# ============================================================

print_context("UPC")
print_context("carton")
print_context("series")


# ============================================================
# SEARCH SCRIPT TAGS
# ============================================================

print("\n" + "=" * 60)
print("SCRIPT TAGS")
print("=" * 60)

scripts = driver.find_elements(
    By.TAG_NAME,
    "script"
)

print(
    "Script tags:",
    len(scripts)
)


for i, script in enumerate(
    scripts
):

    try:

        text = script.get_attribute(
            "innerHTML"
        )

        if not text:
            continue

        lower = text.lower()

        interesting = (
            "upc" in lower
            or "carton" in lower
            or "series" in lower
            or "product" in lower
        )

        if interesting:

            print(
                f"\nSCRIPT #{i}"
            )

            print(
                text[:5000]
            )

    except Exception:
        pass


print("\n" + "=" * 60)
print("DONE")
print("=" * 60)

print("Keep Chrome open.")