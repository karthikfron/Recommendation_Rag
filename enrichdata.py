import json
import requests
import fitz  
import os
from tqdm import tqdm

# Load the JSON data
with open("merged_product_fact_sheet.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Make a folder to store PDFs
os.makedirs("pdfs", exist_ok=True)

# Keywords for metadata extraction
import re

def extract_info_from_text(text):
    text_lower = text.lower()
    duration = ""
    test_type = ""
    remote = "No"
    adaptive = "No"

    # Improved duration matching using regex
    duration_matches = re.findall(r"(\d{1,3})\s*(minutes|min|mins)", text_lower)
    if duration_matches:
        # Grab the first valid match
        duration = duration_matches[0][0] + " mins"

    # Type - still use simple keyword
    for line in text_lower.splitlines():
        if "type" in line and not test_type:
            test_type = line.split("type")[-1].strip(": -").strip()
        if "adaptive" in line and "yes" in line:
            adaptive = "Yes"
        if "remote" in line and "yes" in line:
            remote = "Yes"

    return duration, test_type, remote, adaptive

    lines = text.lower().splitlines()
    duration = ""
    test_type = ""
    remote = "No"
    adaptive = "No"

    for line in lines:
        if "duration" in line and not duration:
            duration = line.split("duration")[-1].strip(": -").strip()
        if "type" in line and not test_type:
            test_type = line.split("type")[-1].strip(": -").strip()
        if "adaptive" in line and "yes" in line:
            adaptive = "Yes"
        if "remote" in line and "yes" in line:
            remote = "Yes"

    return duration, test_type, remote, adaptive

# Iterate and process each product
for item in tqdm(data, desc="Processing PDFs"):
    # Default values
    item["duration"] = ""
    item["type"] = ""
    item["remote"] = ""
    item["adaptive"] = ""

    if item.get("productFactSheet"):
        pdf_url = item["productFactSheet"][0]
        pdf_name = pdf_url.split("/")[-1]
        pdf_path = os.path.join("pdfs", pdf_name)

        # Download PDF if not already downloaded
        if not os.path.exists(pdf_path):
            try:
                response = requests.get(pdf_url)
                with open(pdf_path, "wb") as f:
                    f.write(response.content)
            except Exception as e:
                print(f"Failed to download {pdf_url}: {e}")
                continue

        # Extract text from PDF
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()

            # Extract metadata
            duration, test_type, remote, adaptive = extract_info_from_text(full_text)
            item["duration"] = duration
            item["type"] = test_type
            item["remote"] = remote
            item["adaptive"] = adaptive

        except Exception as e:
            print(f"Failed to extract from {pdf_path}: {e}")
        print(f"{item['title']}: {len(item.get('productFactSheet', []))} PDFs")

# Save the updated JSON
with open("enriched_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("✅ Enrichment complete. Saved to enriched_data.json")
print(f"{item['title']}: {len(item.get('productFactSheet', []))} PDFs")
