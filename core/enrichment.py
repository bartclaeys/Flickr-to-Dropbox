import os
import json
import datetime
import shutil
import piexif
import re
import subprocess
from iptcinfo3 import IPTCInfo
import logging

from core import config

METADATA_DIR = config.METADATA_DIR

def extract_id(filename):
    match = re.search(r'_(\d+)_[a-z0-9]+_o\.', filename)
    if match: return match.group(1)
    match = re.search(r'_(\d+)_o\.', filename)
    if match: return match.group(1)
    match = re.search(r'(\d+)', filename)
    if match: return match.group(1)
    return None

def to_rational(val):
    deg = int(abs(val))
    min = int((abs(val) - deg) * 60)
    sec = round(((abs(val) - deg) * 60 - min) * 60 * 100)
    return [(deg, 1), (min, 1), (sec, 100)]

def enrich_file(file_path, album_name):
    filename = os.path.basename(file_path)
    photo_id = extract_id(filename)
    if not photo_id:
        return False, "Could not extract ID"
        
    json_path = os.path.join(METADATA_DIR, f"photo_{photo_id}.json")
    if not os.path.exists(json_path):
        return False, f"JSON {json_path} not found"

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except Exception as e:
        return False, f"Error reading JSON: {e}"

    # 1. Inject EXIF Metadata (Dates, GPS, Title)
    is_jpeg = file_path.lower().endswith(('.jpg', '.jpeg'))
    if is_jpeg:
        try:
            exif_dict = piexif.load(file_path)
            
            # --- Title Injection ---
            title = meta.get('name', '')
            if title:
                # 0th:ImageDescription (standard)
                exif_dict['0th'][piexif.ImageIFD.ImageDescription] = title.encode('utf-8')
                # 0th:XPTitle (Windows/macOS compatibility) - it's a list of byte integers
                exif_dict['0th'][piexif.ImageIFD.XPTitle] = [ord(c) for c in title] + [0, 0]

            # --- GPS Injection ---
            geo_data = meta.get('geo', [])
            if geo_data and isinstance(geo_data, list) and len(geo_data) > 0:
                geo = geo_data[0]
                lat = float(geo.get('latitude', 0)) / 1000000.0
                lon = float(geo.get('longitude', 0)) / 1000000.0
                
                if lat != 0 or lon != 0:
                    lat_rat, lat_ref = to_rational(lat), ('N' if lat >= 0 else 'S')
                    lon_rat, lon_ref = to_rational(lon), ('E' if lon >= 0 else 'W')
                    gps_ifd = {
                        piexif.GPSIFD.GPSLatitudeRef: lat_ref,
                        piexif.GPSIFD.GPSLatitude: lat_rat,
                        piexif.GPSIFD.GPSLongitudeRef: lon_ref,
                        piexif.GPSIFD.GPSLongitude: lon_rat,
                    }
                    exif_dict["GPS"] = gps_ifd
            
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, file_path)
        except Exception as e:
            print(f"  [WARN] EXIF injection failed for {filename}: {e}")

        # 2. Inject Keyword Tags (IPTC)
        try:
            tags = [t.get('tag', '') for t in meta.get('tags', [])]
            if album_name:
                tags.append(album_name)
            clean_tags = [t.strip() for t in tags if t.strip()]
            
            if clean_tags:
                info = IPTCInfo(file_path, force=True)
                current_keywords = [k.decode('utf-8') if isinstance(k, bytes) else k for k in info['keywords']]
                for tag in clean_tags:
                    if tag not in current_keywords:
                        info['keywords'].append(tag)
                # --- Title in IPTC ---
                if title:
                    info['object name'] = title.encode('utf-8')
                
                info.save()
                if os.path.exists(file_path + "~"):
                    os.remove(file_path + "~")
        except Exception as e:
            print(f"  [WARN] Tags injection failed for {filename}: {e}")

    # 3. Restore Timestamps (Filesystem) - DO THIS LAST
    date_taken = meta.get('date_taken')
    if date_taken:
        try:
            dt = datetime.datetime.strptime(date_taken, "%Y-%m-%d %H:%M:%S")
            touch_str = dt.strftime("%Y%m%d%H%M.%S")
            subprocess.run(['touch', '-t', touch_str, file_path], check=True)
        except Exception as e:
            print(f"  [WARN] Failed to touch {filename}: {e}")

    return True, "Enriched"

def process_album(album_path):
    album_name = os.path.basename(album_path.rstrip('/'))
    print(f"Enriching metadata for album: {album_name}")
    if not os.path.exists(album_path):
        print(f"  [ERR] Path does not exist: {album_path}")
        return
    files = [f for f in os.listdir(album_path) if os.path.isfile(os.path.join(album_path, f))]
    success = 0
    for filename in files:
        file_path = os.path.join(album_path, filename)
        ok, msg = enrich_file(file_path, album_name)
        if ok:
            success += 1
    print(f"Finished. Enriched {success}/{len(files)} files.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        process_album(sys.argv[1])
    else:
        print("Usage: python3 comprehensive_enrichment.py <album_path>")
