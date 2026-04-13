import os

# --- PATH CONFIGURATION ---
# The path where you have extracted your Flickr Data Archive
METADATA_DIR = "Metadata"

# The local path to your Dropbox "Pictures" folder
# Example: "/Users/username/Dropbox/Pictures"
DROPBOX_DIR = "Dropbox_Gallery_Path_Here"

# Temporary directory used for staging files before migration
STAGING_DIR = "Staging"

# --- RECOVERY SETTINGS ---
# Folder to store files that couldn't be automatically matched to metadata
MISSING_METADATA_DIR = os.path.join(STAGING_DIR, "MissingMetadata")

# --- DROPBOX API (Optional for Audit) ---
# Required only if you want to scan for existing cloud folders using tools/audit.py
DROPBOX_ACCESS_TOKEN = "Your_Dropbox_Token_Here"

# --- ANNOTATION DEFAULTS ---
# These are used to generate the MIGRATION_SOURCE.txt files in each album
MIGRATION_SOURCE = "Flickr"
MIGRATION_DATE = "April 12th, 2026"
