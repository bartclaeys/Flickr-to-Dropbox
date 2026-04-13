import os
import json
import re
from core import config

ROOT_DIR = config.DROPBOX_DIR
METADATA_DIR = config.METADATA_DIR

def extract_id(filename):
    match = re.search(r'_(\d+)_[a-z0-9]+_o\.', filename)
    if match: return match.group(1)
    match = re.search(r'_(\d+)_o\.', filename)
    if match: return match.group(1)
    match = re.search(r'(\d+)', filename)
    if match: return match.group(1)
    return None

def update_notes():
    years = [y for y in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, y)) and y.isdigit()]
    
    for year in sorted(years):
        year_path = os.path.join(ROOT_DIR, year)
        albums = [a for a in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, a))]
        
        for album in albums:
            album_path = os.path.join(year_path, album)
            note_path = os.path.join(album_path, "MIGRATION_SOURCE.txt")
            
            # Find a sample photo to get album info
            photos = [f for f in os.listdir(album_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if not photos: continue
            
            p_id = extract_id(photos[0])
            if not p_id: continue
            
            json_path = os.path.join(METADATA_DIR, f"photo_{p_id}.json")
            album_url = "N/A"
            album_name = album
            
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                        album_list = meta.get('albums', [])
                        if album_list:
                            # Try to find the matching album in the metadata list
                            for a_meta in album_list:
                                if a_meta.get('title') == album:
                                    album_url = a_meta.get('url', 'N/A')
                                    break
                            if album_url == "N/A" and album_list:
                                album_url = album_list[0].get('url', 'N/A')
                except:
                    pass

            # Write the enriched note using defaults from config
            content = f"Migration Source: {config.MIGRATION_SOURCE}\n"
            content += f"Migration Date: {config.MIGRATION_DATE}\n"
            content += f"Original Album Title: {album_name}\n"
            content += f"Original Album URL: {album_url}\n"
            content += f"\nMetadata Enrichment Status:\n"
            content += f"- Historical Creation Dates Restored\n"
            content += f"- GPS Geotags Injected\n"
            content += f"- Searchable Keyword Tags Added\n"
            content += f"\nNote: All metadata has been embedded directly into photo headers for future compatibility.\n"

            with open(note_path, 'w') as f:
                f.write(content)
                
    print(f"Finished updating migration notes in all albums.")

if __name__ == "__main__":
    update_notes()
