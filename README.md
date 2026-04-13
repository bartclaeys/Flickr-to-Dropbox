# Flickr to Dropbox Migration & Metadata Preservation

This repository is a practical guide and toolkit for safely moving your entire photo history from Flickr to Dropbox. It is designed to be run on your **local computer**, leveraging the **Dropbox Desktop App** and **Selective Sync** to handle the heavy lifting of uploading thousands of high-resolution memories.

The process is designed around a traditional **Year/Album** organizational structure (e.g., `2024/Summer_Trip`). You do not need to create these year folders beforehand—the scripts will automatically create them for you as it processes your archive.

The AI is best equipped to handle the "Chunking Strategy," monitor your storage levels, and ensure 100% metadata fidelity across thousands of files.

## 🌐 Platform Versatility
While this project is named **Flickr to Dropbox**, the core engine is designed to be **platform agnostic**. 

- **The Enrichment Engine**: The logic for restoring dates, injecting GPS, and embedding titles works perfectly regardless of your final destination (Google Drive, iCloud, OneDrive, or a local NAS).
- **Dropbox Specifics**: The only part of this toolkit specific to Dropbox is the **Cloud Audit (`tools/audit.py`)**. This is used to "see" through Selective Sync to detect duplicates in the cloud. If you are using a different service, you can easily swap this audit tool out or simply rely on the enrichment and organization tools for your local file movement.

## Prerequisites
- **Dropbox Desktop Installed**: The tools rely on your local Dropbox sync client to upload the enriched files.
- **Selective Sync Recommended**: Extremely useful for handling large libraries (100GB+) without filling up your entire hard drive.
- **Dropbox Developer App (Optional)**: Required only if you want to use the cloud audit tools to scan your library for existing remote folders.
- **Python 3.x**: Ensure Python is installed on your machine.

## Key Features
- **Historical Date Restoration**: Fixes the "2026 Date Bug" where photos show the download date instead of the original "Date Taken."
- **Deep Metadata Injection**: Embeds Flickr Titles, Descriptions, Tags, and GPS coordinates directly into EXIF/IPTC headers.
- **Smart Orphan Recovery**: Heuristic matching to identify and restore metadata for files with non-standard names (common with videos).
- **Storage Optimized**: Built specifically to handle libraries that are larger than your local hard drive capacity.
- **Digital Preservation**: Adds a migration source record (`MIGRATION_SOURCE.txt`) to every album for historical record-keeping.

> [!NOTE]
> **Video Metadata**: While photos receive deep internal header injection, video files (MP4/MOV) are restored primarily via filesystem timestamps and organizational folder placement, as video headers have limited metadata support.

## Storage Management (The "Chunking" Strategy)
If your Flickr library is larger than your hard drive, follow this **Batch-and-Sync** approach:
1. **Download in Stages**: Download only a subset of your Flickr zip files at a time.
2. **Process & Move**: Run the tools to enrich and move those albums into your local Dropbox folder.
3. **Wait for Sync**: Let the Dropbox Desktop app upload the files to the cloud.
4. **Offload**: Once synced, use Dropbox's "Selective Sync" (or "Make Online Only") to remove the local copies, freeing up your disk space.
5. **Repeat**: Proceed to the next batch of zip files.

## Step 1: The Flickr Data Export (Manual Step)
The very first step is external to this toolkit and requires patience. You must manually request your data from Flickr:

1. Log in to Flickr and go to **Settings > Your Flickr Data**.
2. Click **"Request my Flickr Data"**.
3. **Wait**: Flickr can take anywhere from a few days to **two weeks** to compile your archives.
4. **Collect Links**: Once your data is ready, Flickr will provide a list of zip files (Photos + Metadata). You will need to copy at least one of these URLs to verify the format, or provide the full list of download links to your AI assistant to handle the batch downloading.

## Workflow & Usage

### 0. Cloud Audit (Optional)
To check if albums already exist in your remote Dropbox (even if they aren't synced locally):
1. Create a Dropbox App at [dropbox.com/developers](https://www.dropbox.com/developers).
2. Generate an Access Token and paste it into `config.py`.
3. Run the audit:
   ```bash
   python3 tools/audit.py
   ```

### 1. Organize & Enrich
Structure your raw Flickr downloads into year folders and inject metadata:
```bash
python3 tools/migrate.py
```

### 2. Annotate
Add migration notes and source URLs to your finished album folders:
```bash
python3 tools/annotate.py
```

### 3. Orphan Recovery
Catch any files that were missed due to non-standard filenames:
```bash
python3 tools/recover.py
```

## Setup
1. **Configure**: Edit `config.py` to point to your local metadata and Dropbox paths. 
   *(Note: Keep this file private on your computer as it contains your local folder paths).*
2. **Install Dependencies**:
   ```bash
   pip install piexif iptcinfo3 dropbox
   ```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
