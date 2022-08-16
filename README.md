# Threat Intelligence Teams Bot

TITB is a fork from Threat Intelligence Discord Bot from vx-underground but for Microsoft Teams and modified to work as an hourly Github-Action 

 
> The vx-underground Threat Intelligence Discord Bot gets updates from various clearnet domains, ransomware threat actor domains This bot will check for updates in intervals of 1800 seconds.

* Written in Python 
* Requires Teams Webhook

# Adding or removing RSS Feeds to monitor
All monitored RSS feeds are in the RssFeedList object. To add a new RSS feed simply append a new entry and assign it a config.txt file entry name. e.g.

In the Python script:
```
    RssFeedList = [["https://grahamcluley.com/feed/", "Graham Cluley"],
                   ["https://1337WebsiteIWannaFollow.com/feed/", "1337Website"]]
```

In the config file:
```
1337Website = ?
```
The "?" indicates it has never received an update.

# Credit
This was made by smelly__vx over a slow and boring weekend. We hope it provides some value to your channel and/or organization.
