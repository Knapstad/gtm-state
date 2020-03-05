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

### Step 1: Google cloud project

First you want to set up your Google cloud Project.
Go to this link [create Google Cloud Project](https://console.cloud.google.com/projectcreate)

![Screenhot of the create new project form](/readme-img/Create-project.png)

Give you project an awsome name and click create.
Remember to set up a billing account if you don't already have one:
[Create a billing account](https://console.cloud.google.com/billing/create)

![Screenshot of the create a blilling account form](/readme-img/createbilling.png)

### Step 2: Set up the API's

There are a couple of API's you need to enable for this project to work.
The Google Tag Manager API and the Google Cloud Functions API.
The easiest way to enable them is to use the search bar on the top of the page.
So with your project selected, search for "Tag manager api":

![Screenshot of the searchbar searched for Tag manager api](/readme-img/Cloud-function-search.png)

Click on Tag manager api and on the new screen click the enable button to enabel the API.

![Screenshot of the enable api screen](/readme-img/Cloud-Api-enable.png)

Do the same for Cloud functions API.

### Step 3: Set up the cloud storage

Now that you have enabled the APIs, you need somewhere to store the data. [Go to Google Cloud Storage]("https://console.cloud.google.com/storage/browser") and click Create Bucket.

![Screenshot of the create bucket dialog](/readme-img/Create-bucket.png)

Chose a uniqe name for your bucket, this name must be globaly uniqe.

![Screenshot of the name feild in thecreate bucket dialog](/readme-img/name-bucket.png)

Next you have to choose a region. You can choose whatever region you want but it will affect your latancy, so it's recomended to choose one that's also awailable for cloud functions. [For a updated list of Cloud Functions locations folow this link](https://cloud.google.com/functions/docs/locations)

![Screenshoot of the location feild in the create bucket dialog](/readme-img/location-bucket.png)

Keep the rest of the settings as the default.
Storage class shuld be Standard, Access control shuld be Fine-grained. And then click Create.

![Screenshot of the remaining create bucket dialog](/readme-img/rest-bucket.png)

