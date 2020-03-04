from google.oauth2 import service_account
import googleapiclient.discovery
import json


with open("config.json") as file:
    config = json.load(file)

GTM_ACCOUNT = config["gtmContainers"][0].split("_")[0]
GTM_CONTAINER = config["gtmContainers"][0].split("_")[1]
SCOPES =["https://www.googleapis.com/auth/tagmanager.readonly","https://www.googleapis.com/auth/devstorage.read_write"] #https://www.googleapis.com/auth/tagmanager.edit.containers'
SERVICE_ACCOUNT_FILE = "obos-225315-4adb95aa0d92.json"
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

data = {}

service = googleapiclient.discovery.build("tagmanager", "v2", credentials =credentials )
client = storage.Client(project="obos",credentials=credentials)


def get_gtm_version_data(service):
    data=service.accounts().containers().versions().live(parent=f"accounts/{GTM_ACCOUNT}/containers/{GTM_CONTAINER}").execute()
    return data

def get_version(data):
    if not data:
        data = get_gtm_version_data()
    return data["containerVersionId"]

def save_version_to_cloud(client, data: str, blob_name: str, bucket_name: str):
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    if not blob:
        blob = bucket.blob(blob_name)
    blob.upload_from_string(data)

def load_version_from_cloud(client, blob_name: str, bucket_name: str):
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    return blob.download_as_string()
