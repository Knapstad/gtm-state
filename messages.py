import requests
import json


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
    if len(message) > 0:
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


def create_new_variable_message(changes):
    if changes.new:
        message = f"## New Variables:"
        for variable in changes.new:
            message += f"\n\n- Id: {variable.id}     Name: {variable.name}"
        return message
    else:
        return ""


def create_removed_variable_message(changes):
    if changes.removed:
        message = f"\n\n## Removed variables:"
        for variable in changes.removed:
            message += f"\n\n- Id: {variable.id}     Name: {variable.name}"
        return message
    else:
        return ""


def create_changed_variable_message(changes):
    if changes.changed:
        message = f"\n\n## Changed tags:"
        for variable in changes.changed:
            message += f"\n\n- Id: {variable.id}     Name: {variable.name}"
        return message
    else:
        return ""


def create_trigger_message(changes):
    message = ""
    message += create_new_trigger_message(changes)
    message += create_changed_trigger_message(changes)
    message += create_removed_trigger_message(changes)
    return message


def create_variable_message(changes):
    message = ""
    message += create_new_variable_message(changes)
    message += create_changed_variable_message(changes)
    message += create_removed_variable_message(changes)
    if len(message) > 0:
        message += "\n\n"
    return message


# def create_slack_message(tag_changes, trigger_changes, data):
#     message = f"New version: {data['containerVersionId']} \nName: {data['name']}\nDescription: {data.get('description', 'No description')}\nLink: {data['tagManagerUrl']}\n"
#     message += create_tag_message(tag_changes).replace("## ", "").replace("\n\n","\n")
#     message += create_trigger_message(trigger_changes).replace("## ", "").replace("\n\n","\n")
#     return message


def create_teams_message(tag_changes, trigger_changes, variable_changes, data):
    message = {
        "title": f"New version published on {data['container']['name']}",
        "text": f"**New version:** {data['containerVersionId']} \n\n**Name:** {data['name']}\n\n**Description:** {data.get('description', 'No description')}\n\n**Link:** {data['tagManagerUrl']}\n\n",
    }
    message["text"] += create_tag_message(tag_changes)
    message["text"] += create_trigger_message(trigger_changes)
    message["text"] += create_variable_message(variable_changes)
    return message


def send_slack_message(hook: str, message: str):
    payload = {"text": message}
    requests.post(hook, data=json.dumps(payload))


def send_teams_message(hook: str, tag_changes, trigger_changes, variable_changes, data):
    payload = create_teams_message(tag_changes, trigger_changes, variable_changes, data)
    requests.post(hook, data=json.dumps(payload)).text
