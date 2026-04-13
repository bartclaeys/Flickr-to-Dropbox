import os
import dropbox
from core import config

def audit_cloud_library():
    """
    Connects to the Dropbox API and lists all folders in the target directory.
    Useful for detecting if Flickr albums already exist in the cloud (even if not synced locally).
    """
    token = config.DROPBOX_ACCESS_TOKEN
    if token == "Your_Dropbox_Token_Here":
        print("Error: Please set your DROPBOX_ACCESS_TOKEN in config.py first.")
        return

    dbx = dropbox.Dropbox(token)
    path = config.DROPBOX_DIR # Root path to your photo library in Dropbox
    
    # Standardize path for API
    api_path = path
    if "/Users/" in path:
        # If user provided a local absolute path, try to extract the Dropbox-relative part
        parts = path.split("/Dropbox/")
        if len(parts) > 1:
            api_path = "/" + parts[1].strip("/")
        else:
            print(f"Warning: Local path {path} doesn't seem to contain '/Dropbox/'.")
            print("The API requires a path relative to your Dropbox root (e.g. '/Pictures').")
            return

    print(f"--- Auditing Dropbox Cloud Path: {api_path} ---")
    
    try:
        found_folders = []
        result = dbx.files_list_folder(api_path, recursive=True)
        
        while True:
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FolderMetadata):
                    found_folders.append(entry.path_display)
            
            if not result.has_more:
                break
            result = dbx.files_list_folder_continue(result.cursor)
            
        print(f"Found {len(found_folders)} folders in the cloud.")
        
        # Save to a report
        report_path = "cloud_audit_report.txt"
        with open(report_path, "w") as f:
            for folder in sorted(found_folders):
                f.write(f"{folder}\n")
        
        print(f"Report saved to {report_path}")
        print("You can now compare this list with your Flickr albums to avoid duplicates.")

    except Exception as e:
        print(f"Error accessing Dropbox API: {e}")

if __name__ == "__main__":
    audit_cloud_library()
