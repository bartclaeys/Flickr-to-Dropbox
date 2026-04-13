# Digital Preservation Strategy

This toolkit follows industrial standards for the long-term preservation of digital photo collections. When migrating assets between platforms (like Flickr to Dropbox), simply moving the files is often insufficient because critical historical context can be lost.

## Why Enhanced Metadata Injection?

### 1. The "2026 Date Bug"
Many cloud export tools (including Flickr's standard downloader) do not preserve the original "Date Taken" in the file's filesystem attributes. This causes photo management software to sort every photo into the year you downloaded them.
- **Our Solution**: We use Python's `datetime` and `subprocess` to perform a precise `touch` command, restoring the original historical timestamp to the file's creation and modification attributes.

### 2. EXIF & IPTC Standardization
Cloud platforms often store photo titles and global coordinates in sidecar JSON files. If you lose those JSONs, you lose your data.
- **EXIF (Exchangeable Image File Format)**: We inject the original Flickr titles and GPS coordinates directly into the photo headers. This makes the data "travel with the file."
- **IPTC (International Press Telecommunications Council)**: We embed your Flickr tags as IPTC Keywords. This ensures that your photos are searchable in Windows Explorer, macOS Finder, Adobe Lightroom, and Google Photos.

### 3. Record Keeping (`MIGRATION_SOURCE.txt`)
Every album folder includes a non-destructive text file detailing the origin of the migration and the status of the metadata enrichment. This ensures that future users (or future AI agents) understand the provenance of the files.
