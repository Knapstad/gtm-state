from google.oauth2 import service_account
from google.cloud import storage
import googleapiclient.discovery
import json
import requests


with open("config.json") as file:
    config = json.load(file)

GTM_ACCOUNT = config["gtm_containers"][0].split("_")[0]
GTM_CONTAINER = config["gtm_containers"][0].split("_")[1]
SCOPES =["https://www.googleapis.com/auth/tagmanager.readonly","https://www.googleapis.com/auth/devstorage.read_write"] #https://www.googleapis.com/auth/tagmanager.edit.containers'
SERVICE_ACCOUNT_FILE = "obos-225315-4adb95aa0d92.json"
CREDENTIALS = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
BLOB_NAME = config["gcs"]["blob_name"]
BUCKET_NAME = config["gcs"]["bucket_name"]
HOOK = config["slack_hook"]
data = {}

service = googleapiclient.discovery.build("tagmanager", "v2", credentials =CREDENTIALS )
client = storage.Client(project="obos",credentials=CREDENTIALS)

def get_gtm_version_data(service):
    data=service.accounts().containers().versions().live(parent=f"accounts/{GTM_ACCOUNT}/containers/{GTM_CONTAINER}").execute()
    return data

def get_version(data) -> str:
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

def send_slack_message(hook, message):
    payload={"text": message}
    requests.post(hook, data=json.dumps(payload))


def check_version():
    data = get_gtm_version_data(service)
    version = get_version(data)
    cloud_version = load_version_from_cloud(client, BLOB_NAME, BUCKET_NAME)
    cloud_version = str(cloud_version,"utf8")

    if cloud_version == version:
        pass
    else:
        message = f"New version: {version} \nName: {data['name']}\nDescription: {data['description'].capitalize()}\nLink: {data['tagManagerUrl']}"
        send_slack_message(HOOK, message)
        save_version_to_cloud(client,version,BLOB_NAME,BUCKET_NAME)

if __name__ == "__main__":
    check_version()
