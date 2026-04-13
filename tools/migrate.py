from core import config

STAGING_DIR = config.STAGING_DIR
DROPBOX_DIR = config.DROPBOX_DIR
ENRICH_SCRIPT = "core/enrichment.py"

def run_command(cmd):
    try:
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"Error running {' '.join(cmd)}: {e}")
        return False

def migrate_full():
    # 1. Process Remaining Staging Albums (2009-2020)
    print("--- Phase 2A: Processing Staging Area ---")
    years = [y for y in os.listdir(STAGING_DIR) if os.path.isdir(os.path.join(STAGING_DIR, y))]
    
    for year in sorted(years):
        if year.startswith(("_", ".")) or year == "MissingMetadata":
            continue
            
        year_path = os.path.join(STAGING_DIR, year)
        albums = [d for d in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, d))]
        
        for album in albums:
            album_path = os.path.join(year_path, album)
            target_year_dir = os.path.join(DROPBOX_DIR, year)
            target_album_path = os.path.join(target_year_dir, album)
            
            # Enrich
            print(f"Enriching: {year}/{album}...")
            run_command(['python3', ENRICH_SCRIPT, album_path])
            
            # Move with conflict check
            os.makedirs(target_year_dir, exist_ok=True)
            if os.path.exists(target_album_path):
                print(f"  [CONFLICT] {year}/{album} already exists in Dropbox. Moving to _Collisions.")
                collision_target = os.path.join(STAGING_DIR, "_Collisions", year, album)
                os.makedirs(os.path.dirname(collision_target), exist_ok=True)
                shutil.move(album_path, collision_target)
            else:
                shutil.move(album_path, target_album_path)
                print(f"  [MOVED] {year}/{album} -> Dropbox")

    # 2. Process Already Moved Dropbox Folders (2000-2008)
    print("\n--- Phase 2B: Enriching Existing Dropbox Folders ---")
    moved_years = [str(y) for y in range(2000, 2009)]
    
    for year in moved_years:
        year_path = os.path.join(DROPBOX_DIR, year)
        if not os.path.exists(year_path):
            continue
            
        print(f"Processing Year: {year}")
        albums = [d for d in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, d))]
        
        for album in albums:
            # We only enrich albums that follow our expected pattern or are subfolders
            # (Basically all of them in these specific year folders)
            album_path = os.path.join(year_path, album)
            print(f"Enriching in-place: {year}/{album}...")
            run_command(['python3', ENRICH_SCRIPT, album_path])

    print("\nFull Migration and Enrichment Complete!")

if __name__ == "__main__":
    migrate_full()
