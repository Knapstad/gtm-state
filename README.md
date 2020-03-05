# The GTM version checker - for google cloud and slack

This script was made by inspiration from [Simo Hava's post on a slack notification system for Google Tag Manager changes](https://www.simoahava.com/analytics/create-slack-notification-system-google-tag-manager-changes/)
It's intended use is as a [Google Cloud Function](https://cloud.google.com/functions/) integrated with [Slack](https://www.slack.com), but you can run the script anywhere you like.

## Requirements

This script requires:

- Python 3.6 or higher
- a Google Tag Manager account
- a Google Cloud account
- a Slack account

## The setup

### Step one Google cloud

First you want to set up your Google cloud Project.
Go to this link [create Google Cloud Project](https://console.cloud.google.com/projectcreate).
![Screenhot of the create new project form](readme-img\Create-project.png)
Give you project an awsome name and click create.
Remember to set up a billing account if you don't already have one
[Create a billing account](https://console.cloud.google.com/billing/create)
![Screenshot of the create a blilling account form](readme-img\createbilling.png)
