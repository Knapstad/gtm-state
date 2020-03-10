# The GTM version checker - for google cloud and slack

This script was made by inspiration from [Simo Hava's post on a slack notification system for Google Tag Manager changes](https://www.simoahava.com/analytics/create-slack-notification-system-google-tag-manager-changes/)
Its intended use is as a [Google Cloud Function](https://cloud.google.com/functions/) integrated with [Slack](https://www.slack.com) and [Microsoft Teams](https://products.office.com/en-us/microsoft-teams/group-chat-software), but you can run the script anywhere you like.

## Requirements

This script requires:

- Python 3.6 or higher
- a Google Tag Manager account
- a Google Cloud account
- a Slack account
- a Teams account

## Example output

This script with this setup will check for changes in your Google Tag Manager container and post the changes to Slack and Microsoft Teams.

Slack:
![Sceen shot of Slack example](/readme-img/slack-example.png)

Teams:
![Screen shot of Teams example](/readme-img/teams-example.png)


## The setup

### Step 1: Google cloud project

First you want to set up your Google cloud Project.
Go to this link [create Google Cloud Project](https://console.cloud.google.com/projectcreate)

![Screenhot of the create new project form](/readme-img/Create-project.png)

Give you project an awesome name and click create.
Remember to set up a billing account if you don't already have one:
[Create a billing account](https://console.cloud.google.com/billing/create)

![Screenshot of the create a blilling account form](/readme-img/createbilling.png)

### Step 2: Set up the API's

There are a couple of APIs' you need to enable for this project to work.
The Google Tag Manager API and the Google Cloud Functions API.
The easiest way to enable them is to use the search bar on the top of the page.
So, with your project selected, search for "Tag manager api":

![Screenshot of the searchbar searched for Tag manager api](/readme-img/Cloud-function-search.png)

Click on Tag manager api and on the new screen click the enable button to enabel the API.

![Screenshot of the enable api screen](/readme-img/Cloud-Api-enable.png)

Do the same for Cloud functions API.

### Step 3: Set up the cloud storage

Now that you have enabled the APIs, you need somewhere to store the data. [Go to Google Cloud Storage]("https://console.cloud.google.com/storage/browser") and click Create Bucket.

![Screenshot of the create bucket dialog](/readme-img/Create-bucket.png)

Chose a uniqe name for your bucket, this name must be globaly uniqe.

![Screenshot of the name feild in thecreate bucket dialog](/readme-img/name-bucket.png)

Next you have to choose a region. You can choose whatever region you want but it will affect your latancy, so it's recomended to choose one that's also awailable for cloud functions. [For an updated list of Cloud Functions locations folow this link](https://cloud.google.com/functions/docs/locations)

![Screenshoot of the location feild in the create bucket dialog](/readme-img/location-bucket.png)

Keep the rest of the settings as the default.
Storage class shuld be Standard, Access control shuld be Fine-grained. And then click Create.

![Screenshot of the remaining create bucket dialog](/readme-img/rest-bucket.png)

### Step 3: Set up Slack

Go to the slack app and in the channel you want to add the messages click the settings cog, and choose add an app.

 ![Screenshot of the add an app dialog in slack app](/readme-img/slack_add_an_app.png)

In the next dialog search for webhook and click install on Incomming Webhook.

![Screenshot of the seachbox and results for webhook](/readme-img/slack-add-web-hook.png)
[Or you can go directly to Slack api page](https://slack.com/apps/A0F7XDUAZ-incoming-webhooks).

On the page click the big add to slack button.
Choose witch channel the webhook shuld connect to and click Add inncomung Webbhooks integration.

![Screenshot of the channel picker dialog](/readme-img/slack-add-web-hook-channel.png)

Copy the webhook url to the config file (We'll go over the config file setup later)
Finnish the setup, you can change the name and add a description and customize an icon for your slack bot.
If you want to customize the messages more, read the documentation linked from that page.

### Step 4: Set up Teams

Open the Teams app and click the elipsies next to the channel you want to add the intigration to and click Conectors.

!["Screenshot of the Teams channel dropdown dialog](/readme-img/teams-add-integration.png)

Next to Inncoming Webhook click configure

!["Screenshot of the add confinguration dialoig for teams](/readme-img/teams-configure.png)

Give it a name and upload a nice icon and click create

!["Screenshot of the configure webhook dialog for teams](/readme-img/teams-configure-name.png)

Copy the webhook url and click done.

### Step 5: Set up cloud credentials

[Go to Google Cloud and find the service accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) Either create a new one or click on the actions of the default one.

![Screenshot of the actions menue on googel cloud service accounts](/readme-img/service-create-key.png)

Choose json in the next dialiog and click create. This will download a file to your machine. Copy this file to the same directory as your other files for this project.

Copy the email from the service account and [add this as a user with read access in GTM](https://tagmanager.google.com/#/admin/)

### Step 6: Set up the config.json

Now it's time to add all our parts to the config file.

```json
{
    "bucket_name": "bucket_name",
    "blob_name": "state.json",
    "gtm_containers": ["accountid_containerid"],
    "slack_hook": "slack_hook_url",
    "microsoft_hook": "microsoft_teams_hook_url",
    "cloud_credetials": "path_to_credentials_file"
}
```

Type in your detail in the config file (im using dummy values)

```json
{
    "bucket_name": "gtm-state",
    "blob_name": "state.json",
    "gtm_containers": ["32154678_156753"],
    "slack_hook": "https://my.slack.hook.com",
    "microsoft_hook": "https://my.microsoft.hook.com",
    "cloud_credetials": "mycredentials.json"
}
```

### Step 7: Setup cloud function

First create a zip file of the project. Make shure you only include main.py, requirements.txt, config.json and your credentialsfile.

[Go to Google Cloud cloud functions](https://console.cloud.google.com/functions/list) and click create function.

![Screen shot of the create cloud function dialog](/readme-img/function-create.png)

In the create function dialog pick a name you like. I went with GTM-version.
Set the memory allocation to 256 or 128, the latter is cheeper.
The trigger shuld be set to Pub/Sub
Add a new topic, I created gtm-version
Under source code choose zip-file
Runtime shuld be Python 3.7
Add your zip-file and sett your bucket as the state bucket.
The function to execute is main.
In the advanced section set the location to the same as you set for your bucket
Click create and your function is done.

![Screen shoot of the terminal with function showing as ok](/readme-img/function-ok.png)

This is what it shuld look like when you have successfully deployed the function

### Step 8: Schedule the funtion

Your function is up, but as for now you need to manually run it. [Head over to the Cloud Scheduler](https://console.cloud.google.com/cloudscheduler). And click create job. Select a location, i selected one close to where my function and bucket lives.

![Screen shot of the select location dialog in google cloud scheduler](/readme-img/scheduler-location.png)

Click next and wait for the process to finnish.

In the next dialiog set a project unique name and you can set a descrtiption if you want.
Frequensy is set using using unix-cron format, I'll run my function every 10 minuets so I'll use `*/10 * * * *`. [If you need or want to read more about the unix-cron format go here](https://cloud.google.com/scheduler/docs/configuring/cron-job-schedules#defining_the_job_schedule)

Set your prefered timezone.

Set the target to Pub/Sub.

Set the topic to the topic you created earlyer.

The payload is set to `true`

Now click create

![Screen shot of the settings dialog for the google cloud Scheduler](/readme-img/scheduler-setup.png)

### Done

You are done. The function will check for updates every 10 minuets and post to Slack and Teams if there are any changes.

