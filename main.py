from google.oauth2 import service_account
from google.cloud import storage
from collections import namedtuple
from functools import wraps
import googleapiclient.discovery
import json
import requests


with open("config.json") as file:
    config = json.load(file)

GTM_ACCOUNT = config["gtm_containers"][0].split("_")[0]
GTM_CONTAINER = config["gtm_containers"][0].split("_")[1]
SCOPES = [
    "https://www.googleapis.com/auth/tagmanager.readonly",
    "https://www.googleapis.com/auth/devstorage.read_write",
]
SERVICE_ACCOUNT_FILE = "obos-225315-4adb95aa0d92.json"
CREDENTIALS = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
BLOB_NAME = config["gcs"]["blob_name"]
BUCKET_NAME = config["gcs"]["bucket_name"]
HOOK = config["slack_hook"]
MICROSOFT = config["microsoft_hook"]
data = {}

service = googleapiclient.discovery.build(
    "tagmanager", "v2", credentials=CREDENTIALS, cache_discovery=False
)
client = storage.Client(project="obos", credentials=CREDENTIALS)

def retry_on_connection_error(max_retry: int = 3):
    def decorate_function(function):
        
        @wraps(function)
        def retry(*args, **kwargs):
            tries = 0
            while tries < max_retry:
                try:
                    return function(*args, **kwargs)
                except ConnectionError:
                    tries += 1
            return function(*args, **kwargs)
        return retry
    return decorate_function

@retry_on_connection_error()
def get_live_version_data(service):
    data = (
        service.accounts()
        .containers()
        .versions()
        .live(parent=f"accounts/{GTM_ACCOUNT}/containers/{GTM_CONTAINER}")
        .execute()
    )
    return data


def get_live_version(data) -> str:
    if not data:
        data = get_live_version_data()
    return data["containerVersionId"]

@retry_on_connection_error()
def save_version_to_cloud(
    client: "google.cloud.storage.client.Client",
    data: str,
    blob_name: str,
    bucket_name: str,
):
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    if not blob:
        blob = bucket.blob(blob_name)
    blob.upload_from_string(data)

@retry_on_connection_error()
def load_version_from_cloud(
    client: "google.cloud.storage.client.Client", 
    blob_name: str, 
    bucket_name: str
):
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    return blob.download_as_string()


@retry_on_connection_error()
def get_version_data(version: str):
    data = (
        service.accounts()
        .containers()
        .versions()
        .get(
            path=f"accounts/{GTM_ACCOUNT}/containers/{GTM_CONTAINER}/versions/{version}"
        )
        .execute()
    )
    return data


def get_tag_changes(live: dict, oldversion: dict):
    tag = namedtuple("tag", "id name")
    live_tags = [tag(i["tagId"], i["name"]) for i in live["tag"]]
    old_tags = [tag(i["tagId"], i["name"]) for i in oldversion["tag"]]
    new = [i for i in live_tags if i not in old_tags]
    removed = [i for i in old_tags if i not in live_tags]
    changed = [
        tag(i["tagId"], i["name"])
        for i in live["tag"]
        for y in oldversion["tag"]
        if y["tagId"] == i["tagId"] and y["fingerprint"] != i["fingerprint"]
    ]
    changes = namedtuple("changes", "new removed changed")
    return changes(new=new, removed=removed, changed=changed)


def get_trigger_changes(live: dict, oldversion: dict):
    trigger = namedtuple("trigger", "id name")
    live_triggers = [trigger(i["triggerId"], i["name"]) for i in live["trigger"]]
    old_triggers = [trigger(i["triggerId"], i["name"]) for i in oldversion["trigger"]]
    new = [i for i in live_triggers if i not in old_triggers]
    removed = [i for i in old_triggers if i not in live_triggers]
    changed = [
        trigger(i["triggerId"], i["name"])
        for i in live["trigger"]
        for y in oldversion["trigger"]
        if y["triggerId"] == i["triggerId"] and y["fingerprint"] != i["fingerprint"]
    ]
    changes = namedtuple("changes", "new removed changed")
    return changes(new=new, removed=removed, changed=changed)


def create_new_tag_message(changes):
    if changes.new:
        message = f"## New tags:"
        for tag in changes.new:
            message += f"\n\n- Id: {tag.id}     Name: {tag.name}"
        return message
    else:
        return ""


def create_removed_tag_message(changes):
    if changes.removed:
        message = f"\n\n## Removed tags:"
        for tag in changes.removed:
            message += f"\n\n- Id: {tag.id}     Name: {tag.name}"
        return message
    else:
        return ""


def create_changed_tag_message(changes):
    if changes.changed:
        message = f"\n\n## Changed tags:"
        for tag in changes.changed:
            message += f"\n\n- Id: {tag.id}     Name: {tag.name}"
        return message
    else:
        return ""

def create_tag_message(changes):
    message = ""
    message += create_new_tag_message(changes)
    message += create_changed_tag_message(changes)
    message += create_removed_tag_message(changes)
    if len(message)>0:
        message += "\n\n"
    return message

def create_new_trigger_message(changes):
    if changes.new:
        message = f"## New triggers:"
        for trigger in changes.new:
            message += f"\n\n- Id: {trigger.id}     Name: {trigger.name}"
        return message
    else:
        return ""


def create_removed_trigger_message(changes):
    if changes.removed:
        message = f"\n\n## Removed triggers:"
        for trigger in changes.removed:
            message += f"\n\n- Id: {trigger.id}     Name: {trigger.name}"
        return message
    else:
        return ""


def create_changed_trigger_message(changes):
    if changes.changed:
        message = f"\n\n## Changed tags:"
        for trigger in changes.changed:
            message += f"\n\n- Id: {trigger.id}     Name: {trigger.name}"
        return message
    else:
        return ""


def create_trigger_message(changes):
    message = ""
    message += create_new_trigger_message(changes)
    message += create_changed_trigger_message(changes)
    message += create_removed_trigger_message(changes)
    return message

def create_slack_message(tag_changes, trigger_changes):
    message = f"New version: {version} \nName: {data['name']}\nDescription: {data['description']}\nLink: {data['tagManagerUrl']}\n"
    message += create_tag_message(tag_changes).replace("## ", "").replace("/n/n","/n")
    message += create_trigger_message(trigger_changes).replace("## ", "").replace("/n/n","/n")
    return message

def create_teams_message(tag_changes, trigger_changes):
    message = {"title": f"New version published", "text": f"**New version:** {version} \n\n**Name:** {data['name']}\n\n**Description:** {data['description']}\n\n**Link:** {data['tagManagerUrl']}\n\n"}
    message["text"] += create_tag_message(tag_changes)
    message["text"] += create_trigger_message(trigger_changes)
    return message

def send_slack_message(hook: str, message: str):
    payload = {"text": message}
    requests.post(HOOK, data=json.dumps(payload))

def send_teams_message(hook: str, message: str):
    payload = create_slack_message(tag_changes, trigger_changes)
    requests.post(MICROSOFT, data=json.dumps(payload)).text

def main(*args, **kwargs):
    #google cloud invokes with 2 arguments, these are not used
    data = get_live_version_data(service)
    version = get_live_version(data)
    cloud_version = load_version_from_cloud(client, BLOB_NAME, BUCKET_NAME)
    cloud_version = str(cloud_version, "utf8")

    if cloud_version == version:
        pass
    else:
        version_data = get_version_data(cloud_version)
        tag_changes = get_tag_changes(data, version_data)
        trigger_changes = get_trigger_changes(data, version_data) 
        message += create_slack_message(tag_changes, trigger_changes)
        send_slack_message(HOOK, message)
        save_version_to_cloud(client, version, BLOB_NAME, BUCKET_NAME)

if __name__ == "__main__":

    main()



