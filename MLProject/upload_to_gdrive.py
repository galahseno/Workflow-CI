import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =============================
# 1. Load GDrive Credentials from ENV
# =============================
creds_json = os.environ.get("GDRIVE_CREDENTIALS")
folder_id = os.environ.get("GDRIVE_FOLDER_ID")

if not creds_json or not folder_id:
    raise ValueError("❌ Missing GDRIVE_CREDENTIALS or GDRIVE_FOLDER_ID environment variables.")

creds = json.loads(creds_json)
credentials = Credentials.from_service_account_info(
    creds,
    scopes=["https://www.googleapis.com/auth/drive"]
)

# =============================
# 2. Setup Google Drive API
# =============================
drive = build('drive', 'v3', credentials=credentials)

def upload_directory(local_dir, parent_id):
    """
    Recursively uploads the contents of a local directory to a Google Drive folder.
    """
    for item in os.listdir(local_dir):
        item_path = os.path.join(local_dir, item)

        if os.path.isdir(item_path):
            # Create corresponding folder on Drive
            folder_metadata = {
                'name': item,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            folder = drive.files().create(
                body=folder_metadata,
                fields='id',
                supportsAllDrives=True
            ).execute()
            print(f"📁 Created folder: {item} (ID: {folder['id']})")

            # Recurse into the subdirectory
            upload_directory(item_path, folder['id'])

        else:
            # Upload the file
            print(f"⬆️ Uploading file: {item_path}")
            file_metadata = {'name': item, 'parents': [parent_id]}
            media = MediaFileUpload(item_path, resumable=True)
            drive.files().create(
                body=file_metadata,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()

# =============================
# 3. Upload All Runs in mlruns/0/
# =============================
mlruns_dir = "./mlruns/0"

for run_id in os.listdir(mlruns_dir):
    run_path = os.path.join(mlruns_dir, run_id)
    if os.path.isdir(run_path):
        # Create a folder with the run_id in Drive
        run_metadata = {
            'name': run_id,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [folder_id]
        }
        run_folder = drive.files().create(
            body=run_metadata,
            fields='id',
            supportsAllDrives=True
        ).execute()

        print(f"\n🚀 Created folder for run_id: {run_id} (ID: {run_folder['id']})")
        upload_directory(run_path, run_folder['id'])

print("\n✅ All MLflow artifacts have been uploaded to Google Drive.")
