from google.oauth2 import service_account
from google.cloud import storage
from collections import namedtuple
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

service = googleapiclient.discovery.build("tagmanager", "v2", credentials=CREDENTIALS, cache_discovery=False)
client = storage.Client(project="obos", credentials=CREDENTIALS, cache_discovery=False)

def get_live_version_data(service):
    data=service.accounts().containers().versions().live(parent=f"accounts/{GTM_ACCOUNT}/containers/{GTM_CONTAINER}").execute()
    return data

def get_live_version(data) -> str:
    if not data:
        data = get_live_version_data()
    return data["containerVersionId"]

def save_version_to_cloud(client: google.cloud.storage.client.Client, data: str, blob_name: str, bucket_name: str):
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    if not blob:
        blob = bucket.blob(blob_name)
    blob.upload_from_string(data)


def load_version_from_cloud(client: google.cloud.storage.client.Client, blob_name: str, bucket_name: str):
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    return blob.download_as_string()

def send_slack_message(hook: str, message: str):
    payload={"text": message}
    requests.post(hook, data=json.dumps(payload))


def main():
    data = get_live_version_data(service)
    version = get_live_version(data)
    cloud_version = load_version_from_cloud(client, BLOB_NAME, BUCKET_NAME)
    cloud_version = str(cloud_version,"utf8")

    if cloud_version == version:
        pass
    else:
        message = f"New version: {version} \nName: {data['name']}\nDescription: {data['description'].capitalize()}\nLink: {data['tagManagerUrl']}"
        send_slack_message(HOOK, message)
        save_version_to_cloud(client,version,BLOB_NAME,BUCKET_NAME)

def get_version_data(version: str):
    data=service.accounts().containers().versions().get(path=f"accounts/{GTM_ACCOUNT}/containers/{GTM_CONTAINER}/versions/{version}").execute()
    return data

def get_tag_changes(live: dict, oldversion: dict):
    tag = namedtuple("tag","id name")
    live_tags = [tag(i["tagId"], i["name"]) for i in live["tag"]]
    old_tags = [tag(i["tagId"], i["name"]) for i in oldversion["tag"]]
    new = [i for i in live_tags if i not in old_tags]
    removed = [i for i in old_tags if i not in live_tags]
    changed = [tag(i["tagId"], i["name"]) for i in live["tag"] for y in oldversion["tag"] if y["tagId"]==i["tagId"] and y["fingerprint"] != i["fingerprint"] ]
    changes = namedtuple("changes", "new removed changed")
    return changes(new=new, removed=removed, changed=changed)

def get_trigger_changes(live: dict, oldversion: dict):
    trigger = namedtuple("trigger","id name")
    live_triggers = [trigger(i["triggerId"], i["name"]) for i in live["trigger"]]
    old_triggers = [trigger(i["triggerId"], i["name"]) for i in oldversion["trigger"]]
    new = [i for i in live_triggers if i not in old_triggers]
    removed = [i for i in old_triggers if i not in live_triggers]
    changed = [trigger(i["triggerId"], i["name"]) for i in live["trigger"] for y in oldversion["trigger"] if y["triggerId"]==i["triggerId"] and y["fingerprint"] != i["fingerprint"] ]
    changes = namedtuple("changes", "new removed changed")
    return changes(new=new, removed=removed, changed=changed)

def create_new_tag_message(changes):
    if changes.new:
        message=f"New tags:"
        for tag in changes.new:
            message +=f"\nId: {tag.id}     Name: {tag.name}"
        return message

def create_removed_tag_message(changes):
    if changes.removed:
        message=f"\n\nRemoved tags:"
        for tag in changes.removed:
            message +=f"\nId: {tag.id}     Name: {tag.name}"
        return message

def create_changed_tag_message(changes):
    if changes.changed:
        message=f"\n\nChanged tags:"
        for tag in changes.changed:
            message +=f"\nId: {tag.id}     Name: {tag.name}"
        return message

def create_tag_message(changes):
    message = ""
    message += create_new_tag_message(changes)
    message += create_changed_tag_message(changes)
    message += create_removed_tag_message(changes)
    return message

def retry_on_connection_error(function, max_retry: int = 3):
    retries = 0
    while retries < max_retry:
        try:
            return function()
        except ConnectionError:
            retries += 1

if __name__ == "__main__":

    main()