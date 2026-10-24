"""
IPL Analytics Pro - Dataset Acquisition Script
Downloads IPL ball-by-ball and match dataset from Cricsheet.
URL: https://cricsheet.org/downloads/ipl_csv2.zip
License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""

import os
import sys
import json
import zipfile
import urllib.request
from datetime import datetime
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
MANIFEST_PATH = os.path.join(RAW_DIR, "data_manifest.json")
ZIP_PATH = os.path.join(RAW_DIR, "ipl_csv2.zip")
EXTRACT_DIR = os.path.join(RAW_DIR, "ipl_csv2")

CRICSHEET_URL = "https://cricsheet.org/downloads/ipl_csv2.zip"

def ensure_dirs():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(EXTRACT_DIR, exist_ok=True)

def download_dataset():
    print(f"Connecting to {CRICSHEET_URL}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(CRICSHEET_URL, headers=headers)
    
    with urllib.request.urlopen(req) as response:
        total_size = int(response.headers.get("Content-Length", 0))
        last_modified = response.headers.get("Last-Modified", "Unknown")
        print(f"File size: {total_size / (1024 * 1024):.2f} MB")
        print(f"Server Last-Modified: {last_modified}")
        
        with open(ZIP_PATH, "wb") as f:
            downloaded = 0
            chunk_size = 65536
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    pct = (downloaded / total_size) * 100
                    print(f"\rDownloading: {pct:.1f}% ({downloaded / (1024*1024):.2f} MB)", end="")
            print("\nDownload complete.")
            
    return last_modified, os.path.getsize(ZIP_PATH)

def extract_and_manifest(last_modified, file_size):
    print("Extracting archive...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)
        namelist = zip_ref.namelist()
        
    csv_files = [f for f in namelist if f.endswith(".csv") and not f.startswith("README")]
    print(f"Extracted {len(namelist)} items ({len(csv_files)} match CSVs).")
    
    # Read the README file if present
    readme_path = os.path.join(EXTRACT_DIR, "README.txt")
    readme_content = ""
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
            readme_content = f.read()
            
    manifest = {
        "dataset_name": "Cricsheet IPL Ball-by-Ball and Match Data (CSV2 Format)",
        "source_url": CRICSHEET_URL,
        "license": "Creative Commons Attribution-ShareAlike (CC BY-SA 4.0)",
        "download_timestamp": datetime.now().isoformat(),
        "server_last_modified": last_modified,
        "archive_size_bytes": file_size,
        "total_extracted_files": len(namelist),
        "total_match_csvs": len(csv_files),
        "readme_notes": readme_content[:500] if readme_content else None
    }
    
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Saved manifest to {MANIFEST_PATH}")
    return manifest

if __name__ == "__main__":
    ensure_dirs()
    last_mod, size = download_dataset()
    manifest = extract_and_manifest(last_mod, size)
    print("Dataset acquisition finished successfully.")
