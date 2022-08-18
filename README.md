# 🏴‍☠️🤖 Threat Intelligence Teams Bot

TITB is a fork from [Threat Intelligence Discord Bot from vx-underground](https://github.com/vxunderground/ThreatIntelligenceDiscordBot/) but for Microsoft Teams and modified to work as an hourly Github-Action 

> The vx-underground Threat Intelligence Discord Bot gets updates from various clearnet domains, ransomware threat actor domains This bot will check for updates in intervals of 1800 seconds.

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  [![Twitter: JMousqueton](https://img.shields.io/twitter/follow/JMousqueton.svg?style=social)](https://twitter.com/JMousqueton) ![Last Run](https://github.com/JMousqueton/CTI-MSTeams-Bot/actions/workflows/fetchCTI.yml/badge.svg)

## Description

* Written in Python 
* Requires Teams Webhook

Threat Intelligence Teams Bot gets updates from various clearnet domains and ransomware threat actor domains. 

This bot will check for updates hourly. 

TITB doesn't need any server, it works as a GitHub-Action : see the [fetchCTI.yml](.github/workflows/fetchCTI.yml) file.

I've decided to remove the TelegramBot because it was not relevant for my needs. 

## Installation
Install all the modules in ```requirements.txt```
```
pip3 install -r requirements.txt
```

## Configuration

* Create a MS-Teams WebHook  
* in an environment you will called `CI`, paste the created webhook url in a `MSTEAMS_WEBHOOK` variable. 

## Adding or removing RSS Feeds to monitor
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

## Sources 

I've added the following sources : 

* FR-CERT Avis (aka [ANSSI](https://www.ssi.gouv.fr/)) : notifications from gov French CERT 
* FR-CERT Alertes (aka [ANSSI](https://www.ssi.gouv.fr/)) : Alerts from gov French CERT 
* [Leak-lookup](https://leak-lookup.com/): Leak notification 
* [Cyber-News](https://www.cyber-news.fr)

## ToDo 

* Extract the RSS Feed from the main program to an external configuration files. 
* Add more sources

## Credit
This was made by smelly__vx over a slow and boring weekend. We hope it provides some value to your channel and/or organization.
