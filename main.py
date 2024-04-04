from google.oauth2 import service_account
from google.cloud import storage
from collections import namedtuple
from functools import wraps
from messages import *
import googleapiclient.discovery
import requests
import json


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
def get_live_version_data(service, GTM_ACCOUNT, GTM_CONTAINER):
    version = (
        service.accounts()
        .containers()
        .versions()
        .live(parent=f"accounts/{GTM_ACCOUNT}/containers/{GTM_CONTAINER}")
        .execute()
    )
    return version


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
    blob.upload_from_string(json.dumps(data))


@retry_on_connection_error()
def load_version_from_cloud(
    client: "google.cloud.storage.client.Client", blob_name: str, bucket_name: str
):
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    return blob.download_as_string()


@retry_on_connection_error()
def get_version_data(service, version: str, GTM_ACCOUNT: str, GTM_CONTAINER: str):
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


def get_variable_changes(live: dict, oldversion: dict):
    variable = namedtuple("variable", "id name")
    live_tags = [variable(i["variableId"], i["name"]) for i in live["variable"]]
    old_tags = [variable(i["variableId"], i["name"]) for i in oldversion["variable"]]
    new = [i for i in live_tags if i not in old_tags]
    removed = [i for i in old_tags if i not in live_tags]
    changed = [
        variable(i["variableId"], i["name"])
        for i in live["variable"]
        for y in oldversion["variable"]
        if y["variableId"] == i["variableId"] and y["fingerprint"] != i["fingerprint"]
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


def main(*args, **kwargs):
    with open("config.json") as file:
        config = json.load(file)
        SCOPES = [
            "https://www.googleapis.com/auth/tagmanager.readonly",
            "https://www.googleapis.com/auth/devstorage.read_write",
        ]
        SERVICE_ACCOUNT_FILE = config["cloud_credetials"]

        BLOB_NAME = config["blob_name"]
        BUCKET_NAME = config["bucket_name"]
        HOOK = config["slack_hook"]
        MICROSOFT = config["microsoft_hook"]
        CREDENTIALS = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = googleapiclient.discovery.build(
            "tagmanager", "v2", credentials=CREDENTIALS, cache_discovery=False
        )
        client = storage.Client(credentials=CREDENTIALS)
        accounts = service.accounts().list().execute()
        containers = [
            service.accounts()
            .containers()
            .list(parent=account["path"])
            .execute()["container"]
            for account in accounts["account"]
        ]
        # flatten containers list
        containers = [item for sublist in containers for item in sublist]
        cloud_version = load_version_from_cloud(client, BLOB_NAME, BUCKET_NAME)
        cloud_version = json.loads(str(cloud_version, "utf8"))

        for container in containers:
            GTM_ACCOUNT = container["accountId"]
            GTM_CONTAINER = container["containerId"]
            data = {}
            data = get_live_version_data(service, GTM_ACCOUNT, GTM_CONTAINER)
            version = get_live_version(data)

            if cloud_version[f"{GTM_ACCOUNT}_{GTM_CONTAINER}"] == version:
                pass

            else:
                version_data = get_version_data(
                    service,
                    cloud_version[f"{GTM_ACCOUNT}_{GTM_CONTAINER}"],
                    GTM_ACCOUNT,
                    GTM_CONTAINER,
                )
                tag_changes = get_tag_changes(data, version_data)
                trigger_changes = get_trigger_changes(data, version_data)
                variable_changes = get_variable_changes(data, version_data)
                # message = create_slack_message(tag_changes, trigger_changes, variable_changes, data)
                send_teams_message(
                    MICROSOFT, tag_changes, trigger_changes, variable_changes, data
                )
                # send_slack_message(HOOK, message)
                cloud_version[f"{GTM_ACCOUNT}_{GTM_CONTAINER}"] = version
                save_version_to_cloud(client, cloud_version, BLOB_NAME, BUCKET_NAME)


if __name__ == "__main__":

    main()
