import csv
import os
import re
import requests
from urllib.parse import unquote, urlparse

# Resolve paths from this file so the script works from any cwd.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to your CSV file
CSV_PATH = os.path.join(BASE_DIR, "laws.csv")

# Folder where PDFs will be saved
OUTPUT_DIR = os.path.join(BASE_DIR, "pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def sanitize_filename(name):
    name = (name or "").strip().replace(" ", "_").replace("/", "-")
    # Remove Windows-invalid filename characters.
    name = re.sub(r'[<>:"\\|?*]', "", name)
    return name.strip("._")


def get_real_pdf_name(response, fallback_name):
    # Prefer filename from Content-Disposition, fallback to final URL path.
    content_disposition = response.headers.get("Content-Disposition", "")

    filename = ""
    if "filename*=" in content_disposition:
        value = content_disposition.split("filename*=", 1)[1].split(";", 1)[0].strip()
        if "''" in value:
            value = value.split("''", 1)[1]
        filename = unquote(value.strip('"'))
    elif "filename=" in content_disposition:
        value = content_disposition.split("filename=", 1)[1].split(";", 1)[0].strip()
        filename = value.strip('"')

    if not filename:
        parsed = urlparse(response.url or "")
        filename = unquote(os.path.basename(parsed.path))

    if not filename:
        filename = fallback_name

    filename = sanitize_filename(filename)
    if not filename.lower().endswith(".pdf"):
        filename = f"{filename}.pdf"

    return filename


def download_pdf(url, output_dir, fallback_name):
    try:
        response = requests.get(url, timeout=30)
        # If response is successful
        if response.status_code == 200:
            real_filename = get_real_pdf_name(response, fallback_name)
            file_path = os.path.join(output_dir, real_filename)

            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {file_path}")
            return real_filename
        else:
            print(f"Failed to download (status {response.status_code}): {url}")
            return ""
    except Exception as err:
        print(f"Error downloading {url} -> {err}")
        return ""

def main():
    with open(CSV_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    for row in rows:
        name = row.get("PDF_Name", "").strip()
        pdf_url = row.get("PDF_Link", "").strip()
        if not pdf_url:
            continue

        # Keep fallback deterministic if CSV name is missing.
        fallback_name = sanitize_filename(name) or "downloaded_file.pdf"
        if not fallback_name.lower().endswith(".pdf"):
            fallback_name = f"{fallback_name}.pdf"

        downloaded_name = download_pdf(pdf_url, OUTPUT_DIR, fallback_name)
        if downloaded_name:
            row["PDF_Name"] = downloaded_name

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("CSV updated with downloaded PDF names.")

if __name__ == "__main__":
    main()
