from core import config
from core.enrichment import enrich_file

SOURCE_DIR = config.MISSING_METADATA_DIR
DROPBOX_ROOT = config.DROPBOX_DIR
METADATA_DIR = config.METADATA_DIR

def smart_extract_id(filename):
    # 1. Try standard Flickr photo: name_ID_secret_o.jpg
    match = re.search(r'_(\d+)_[a-z0-9]+_o\.', filename)
    if match: return match.group(1)
    
    # 2. Try ID at the very end before extension (common for videos and descriptive names)
    # This is better for vid_YYYYMMDD_HHMMSS_ID.mp4
    match = re.search(r'_(\d+)\.[^.]+$', filename)
    if match: return match.group(1)
    
    # 3. Try ID at the start: ID_secret_o.jpg
    match = re.search(r'^(\d+)_', filename)
    if match: return match.group(1)

    # 4. Try any 10-11 digit sequence that ISN'T at the start of a date string
    # (Actually, let's just look for the last 10-11 digit sequence)
    all_matches = re.findall(r'(\d{10,11})', filename)
    if all_matches:
        return all_matches[-1] # Return the LAST one found, which is usually the ID
    
    return None

def recover():
    if not os.path.exists(SOURCE_DIR):
        print(f"Source dir {SOURCE_DIR} not found.")
        return

    files = [f for f in os.listdir(SOURCE_DIR) if os.path.isfile(os.path.join(SOURCE_DIR, f))]
    print(f"Found {len(files)} files to recover in {SOURCE_DIR}.")
    
    success = 0
    skipped = []

    for filename in sorted(files):
        file_path = os.path.join(SOURCE_DIR, filename)
        photo_id = smart_extract_id(filename)
        
        if not photo_id:
            # Fallback: Check if filename contains a year
            year_match = re.search(r'20(0[0-9]|1[0-9]|20)', filename)
            if year_match:
                year = year_match.group(0)
                target_dir = os.path.join(DROPBOX_ROOT, year, "Uncategorized")
                os.makedirs(target_dir, exist_ok=True)
                shutil.move(file_path, os.path.join(target_dir, filename))
                print(f"  [HEURISTIC] {filename} -> {year}/Uncategorized")
                success += 1
                continue
            
            print(f"  [FAIL] Could not find ID for {filename}")
            skipped.append(filename)
            continue

        json_path = os.path.join(METADATA_DIR, f"photo_{photo_id}.json")
        if not os.path.exists(json_path):
            print(f"  [FAIL] JSON for ID {photo_id} not found ({filename})")
            skipped.append(filename)
            continue

        # Load JSON to get year and album
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
                
            date_taken = meta.get('date_taken', 'Unknown')
            year = "Unknown"
            if date_taken != 'Unknown':
                year = date_taken.split('-')[0]
            
            album_list = meta.get('albums', [])
            album_name = "Uncategorized"
            if album_list:
                album_name = album_list[0].get('title', 'Uncategorized')

            print(f"Recovering {filename} (ID: {photo_id})...")
            
            # 1. Enrich (only for images)
            import comprehensive_enrichment
            comprehensive_enrichment.METADATA_DIR = METADATA_DIR
            comprehensive_enrichment.enrich_file(file_path, album_name)
            
            # 2. Move to Target
            target_year_dir = os.path.join(DROPBOX_ROOT, year)
            target_dir = os.path.join(target_year_dir, album_name)
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, filename)
            
            if os.path.exists(target_path):
                # If it's the exact same file, we can remove the orphan
                print(f"  [CONFLICT] {filename} already exists. Cleaning up orphan.")
                os.remove(file_path)
                success += 1
            else:
                shutil.move(file_path, target_path)
                print(f"  [SUCCESS] -> {year}/{album_name}/")
                success += 1
                
        except Exception as e:
            print(f"  [ERR] {filename}: {e}")
            skipped.append(filename)

    print(f"\nRecovery Finished.")
    print(f"Successfully recovered: {success}")
    if skipped:
        print(f"Still Skipped {len(skipped)} files:")
        for s in skipped:
            print(f" - {s}")

if __name__ == "__main__":
    recover()
