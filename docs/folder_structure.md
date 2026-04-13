# Recommended Folder Structure

This project is optimized for a **Year-Based** library organization. This structure is the most stable and compatible format for long-term digital archiving, as it scales gracefully from hundreds to hundreds of thousands of files.

## High-Level View
We recommend the following hierarchy within your Dropbox "Pictures" or "Photos" directory:

```text
Dropbox/
├── Pictures/
│   ├── 2024/
│   │   ├── Summer_Trip/
│   │   ├── Tokyo/
│   │   └── MIGRATION_SOURCE.txt
│   ├── 2025/
│   │   ├── Iceland Roadtrip/
│   │   └── MIGRATION_SOURCE.txt
│   └── Uncategorized/
```

## Organizational Rules

### 1. Year Folders (`YYYY`)
The top-level division should always be the year. This prevents any single folder from becoming too large and makes selective sync much easier to manage. If you have 50GB of photos in 2024 but only 2GB in 2025, you can offload the entire 2024 folder to the cloud while keeping 2025 local.

### 2. Album Folders
Inside each year, files are grouped by Flickr Album name. 
- **Migration Source File**: Our `tools/annotate.py` script places a `MIGRATION_SOURCE.txt` file inside these folders so that the origin of the assets is always documented.

### 3. The "Uncategorized" Folder
Any photos that were not part of a Flickr Album or were recovered via the "Orphan Recovery" process are placed in a `YYYY/Uncategorized` folder. This ensures that every file is at least sorted by time, even if its original context was lost.
