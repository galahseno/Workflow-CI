import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import mlflow
from mlflow.tracking import MlflowClient

# 1. Load Google Drive credentials
creds = json.loads(os.environ["GDRIVE_CREDENTIALS"])
credentials = Credentials.from_service_account_info(
    creds,
    scopes=["https://www.googleapis.com/auth/drive"]
)

# 2. Build Drive API client
service = build('drive', 'v3', credentials=credentials)
SHARED_DRIVE_ID = os.environ["GDRIVE_FOLDER_ID"]

# 3. Setup MLflow tracking
mlflow.set_tracking_uri("file:///tmp/mlruns")
client = MlflowClient()

# 4. Get latest run from the experiment
experiment = client.get_experiment_by_name("Cardiovascular_Classifier")
if experiment is None:
    raise Exception("Experiment not found.")

runs = client.search_runs(experiment_ids=[experiment.experiment_id], order_by=["start_time DESC"], max_results=1)
if not runs:
    raise Exception("No runs found.")

latest_run = runs[0]
run_id = latest_run.info.run_id
artifact_uri = latest_run.info.artifact_uri  # e.g., file:///tmp/mlruns/0/<run_id>/artifacts

# Convert artifact_uri to local path
local_artifact_path = artifact_uri.replace("file://", "")
print(f"📦 Found latest run_id: {run_id}")
print(f"📁 Local artifact path: {local_artifact_path}")

def upload_directory(local_dir_path, parent_drive_id):
    for item_name in os.listdir(local_dir_path):
        item_path = os.path.join(local_dir_path, item_name)
        if os.path.isdir(item_path):
            folder_meta = {
                'name': item_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_drive_id]
            }
            created_folder = service.files().create(
                body=folder_meta,
                fields='id',
                supportsAllDrives=True
            ).execute()
            new_folder_id = created_folder["id"]
            print(f"Created folder: {item_name} (ID: {new_folder_id})")

            upload_directory(item_path, new_folder_id)
        else:
            print(f"Uploading file: {item_name}")
            file_meta = {
                'name': item_name,
                'parents': [parent_drive_id]
            }
            media = MediaFileUpload(item_path, resumable=True)
            service.files().create(
                body=file_meta,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()

# 5. Create folder in Drive using run_id
folder_metadata = {
    'name': run_id,
    'mimeType': 'application/vnd.google-apps.folder',
    'parents': [SHARED_DRIVE_ID]
}
run_drive_folder = service.files().create(
    body=folder_metadata,
    fields='id',
    supportsAllDrives=True
).execute()
run_drive_folder_id = run_drive_folder["id"]

# 6. Upload local artifacts to Drive
upload_directory(local_artifact_path, run_drive_folder_id)

print("✅ Upload completed to Google Drive.")
