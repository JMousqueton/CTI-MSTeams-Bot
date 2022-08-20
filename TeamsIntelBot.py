#!/usr/bin/env python3  
# -*- coding: utf-8 -*- 
#----------------------------------------------------------------------------
# Created By  : Julien Mousqueton @JMousqueton
# Original By : VX-Underground 
# Created Date: 18/08/2022
# version     : 1.6.1
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Imports 
# ---------------------------------------------------------------------------
import feedparser
import time
import csv
from configparser import ConfigParser
import requests
import urllib.request, json
import os #for github action 

ConfigurationFilePath = "./Config.txt" ##path to configuration file

FileConfig = ConfigParser()
FileConfig.read(ConfigurationFilePath)


# ---------------------------------------------------------------------------
# Get Microsoft Teams Webhook from Github Action CI:Env.  
# ---------------------------------------------------------------------------
Url=os.getenv('MSTEAMS_WEBHOOK')


# ---------------------------------------------------------------------------
# Function to send MS-Teams card 
# ---------------------------------------------------------------------------
def send_teams(webhook_url:str, content:str, title:str, color:str="000000") -> int:
    """
      - Send a teams notification to the desired webhook_url
      - Returns the status code of the HTTP request
        - webhook_url : the url you got from the teams webhook configuration
        - content : your formatted notification content
        - title : the message that'll be displayed as title, and on phone notifications
        - color (optional) : hexadecimal code of the notification's top line color, default corresponds to black
    """
    response = requests.post(
        url=webhook_url,
        headers={"Content-Type": "application/json"},
        json={
            "themeColor": color,
            "summary": title,
            "sections": [{
                "activityTitle": title,
                "activitySubtitle": content
            }],
        },
    )
    return response.status_code # Should be 200


# ---------------------------------------------------------------------------
# Fetch Ransomware attacks from https://ransomwatch.mousqueton.io  
# ---------------------------------------------------------------------------
def FnGetRansomwareUpdates():
    
    OutputString = ""

    with urllib.request.urlopen("https://raw.githubusercontent.com/jmousqueton/ransomwatch/main/posts.json") as RansomwareUrl:
        Data = json.loads(RansomwareUrl.read().decode())
        for Entries in Data:

            DateActivity = Entries["discovered"]
            TmpObject = FileConfig.get('main', Entries["group_name"])

            if "?" in TmpObject:
                FileConfig.set('main', Entries["group_name"], DateActivity)

            if(TmpObject >= DateActivity):
                continue
            else:
                FileConfig.set('main', Entries["group_name"], Entries["discovered"])
            
            OutputMessage = "Group : <b>"
            OutputMessage += Entries["group_name"]
            OutputMessage += "</b><br>🗓 "
            OutputMessage += Entries["discovered"]
            OutputMessage += "</b><br>🌍 <a href=\"https://www.google.com/search?q="
            OutputMessage += Entries["post_title"]
            OutputMessage += "\">"
            OutputMessage += Entries["post_title"]
            OutputMessage += "</a>"
            Title = "🏴‍☠️ 🔒 "           
            Title += Entries["post_title"] 
            send_teams(Url,OutputMessage,Title)
            time.sleep(3)

            FileConfig.set('main', Entries["group_name"], Entries["discovered"])

    with open(ConfigurationFilePath, 'w') as FileHandle:
        FileConfig.write(FileHandle)


# ---------------------------------------------------------------------------
# Function fetch RSS feeds  
# ---------------------------------------------------------------------------
def FnGetRssFromUrl(RssItem):
    NewsFeed = feedparser.parse(RssItem[0])
    DateActivity = ""
    IsInitialRun = False

    LastSaved = FileConfig.get('main', RssItem[1])

    for RssObject in NewsFeed.entries:

        try:
            DateActivity = time.strftime('%Y-%m-%dT%H:%M:%S', RssObject.published_parsed)
        except: 
            DateActivity = time.strftime('%Y-%m-%dT%H:%M:%S', RssObject.updated_parsed)
        
        TmpObject = FileConfig.get('main', RssItem[1])
        if "?" in TmpObject:
            IsInitialRun = True
            FileConfig.set('main', RssItem[1], DateActivity)

        if IsInitialRun is False:
            if(TmpObject >= DateActivity):
                continue
            else:
                FileConfig.set('main', RssItem[1], DateActivity)

        OutputMessage = "Date: " + DateActivity
        OutputMessage += "<br>"
        OutputMessage += "Title:<b> " + RssObject.title
        OutputMessage += "</b><br>"
        OutputMessage += "Read more: " + RssObject.link
        OutputMessage += "<br>"

        # Nice emoji :) 
        match RssItem[1]:
            case "Leak-Lookup":
                Title = '💧 '
            case "FR-CERT Alertes" | "FR-CERT Avis":
                Title = '🇫🇷 '
            case "EU-ENISA Publications":
                Title = '🇪🇺 '
            case "Cyber-News":
                Title = '🕵🏻‍♂️ '
            case "Bleeping Computer":
                Title = '💻 '
            case "Microsoft Sentinel":
                Title = '🔭 '
            case "Hacker News":
                Title = '📰 '
            case "ATT":
                Title = '📞 '
            case "VirusBulletin":
                Title = '🦠 '
            case "US-CERT CISA":
                Title = '🇺🇸 '
            case "NCSC":
                Title = '🇬🇧 '
             case "SANS":
                Title = '🌍 '
            case _:
                Title = '📢 '

        Title += RssItem[1]
        send_teams(Url,OutputMessage,Title)
        time.sleep(3)

    with open(ConfigurationFilePath, 'w') as FileHandle:
        FileConfig.write(FileHandle)

    IsInitialRun = False


# ---------------------------------------------------------------------------
# Log  
# ---------------------------------------------------------------------------
def FnCreateLogString(RssItem):
    LogString = "[*]" + time.ctime()
    LogString += " " + "checked " + RssItem
    print(LogString)
    time.sleep(2) 


# ---------------------------------------------------------------------------
# Main function  
# ---------------------------------------------------------------------------    
def EntryMain():

    LogString = ""
    
    with open('Feed.csv', newline='') as f:
        reader = csv.reader(f)
        RssFeedList = list(reader)
            
    for RssItem in RssFeedList:
        FnGetRssFromUrl(RssItem)
        FnCreateLogString(RssItem[1])

    FnGetRansomwareUpdates()
    FnCreateLogString("Ransomware List")


# ---------------------------------------------------------------------------
# Main 
# ---------------------------------------------------------------------------

EntryMain()
