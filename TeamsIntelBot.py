#!/usr/bin/env python3  
# -*- coding: utf-8 -*- 
#----------------------------------------------------------------------------
# Created By  : Julien Mousqueton @JMousqueton
# Original By : VX-Underground 
# Created Date: 18/08/2022
# version     : 1.7.1
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Imports 
# ---------------------------------------------------------------------------
import feedparser
import time
import csv # Feed.csv
import sys # Python version 
import json # Ransomware feed via ransomwatch 
from configparser import ConfigParser
import requests
import os # Webhook OS Variable and Github action 

# ---------------------------------------------------------------------------
# Read the Config.txt file   
# ---------------------------------------------------------------------------
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
def Send_Teams(webhook_url:str, content:str, title:str, color:str="000000") -> int:
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
def GetRansomwareUpdates():
    
    Data = requests.get("https://raw.githubusercontent.com/jmousqueton/ransomwatch/main/posts.json")
        
    for Entries in Data.json():

        DateActivity = Entries["discovered"]
            
        # Correction for issue #1 : https://github.com/JMousqueton/CTI-MSTeams-Bot/issues/1
        try:
            TmpObject = FileConfig.get('main', Entries["group_name"])
        except:
            FileConfig.set('main', Entries["group_name"], " = ?")
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
        OutputMessage += Entries["post_title"].replace("*.", "")
        OutputMessage += "\">"
        OutputMessage += Entries["post_title"]
        OutputMessage += "</a>"
        
        Title = "🏴‍☠️ 🔒 "     
        Title += Entries["post_title"].replace("*.", "") 
        
        Send_Teams(Url,OutputMessage,Title)
        #DEBUG# print(Title)
        time.sleep(3)

        FileConfig.set('main', Entries["group_name"], Entries["discovered"])

    with open(ConfigurationFilePath, 'w') as FileHandle:
        FileConfig.write(FileHandle)


# ---------------------------------------------------------------------------
# Function fetch RSS feeds  
# ---------------------------------------------------------------------------
def GetRssFromUrl(RssItem):
    NewsFeed = feedparser.parse(RssItem[0])
    DateActivity = ""
    IsInitialRun = False

    for RssObject in NewsFeed.entries:

        try:
            DateActivity = time.strftime('%Y-%m-%dT%H:%M:%S', RssObject.published_parsed)
        except: 
            DateActivity = time.strftime('%Y-%m-%dT%H:%M:%S', RssObject.updated_parsed)
        
        # Correction for issue #1 : https://github.com/JMousqueton/CTI-MSTeams-Bot/issues/1
        try:
            TmpObject = FileConfig.get('main', RssItem[1])
        except:
            FileConfig.set('main', RssItem[1], " = ?")
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
        Send_Teams(Url,OutputMessage,Title)
        #DEBUG# print(Title)
        time.sleep(3)

    with open(ConfigurationFilePath, 'w') as FileHandle:
        FileConfig.write(FileHandle)


# ---------------------------------------------------------------------------
# Log  
# ---------------------------------------------------------------------------
def CreateLogString(RssItem):
    LogString = "[*]" + time.ctime()
    LogString += " " + "checked " + RssItem
    print(LogString)
    time.sleep(2) 


# ---------------------------------------------------------------------------
# Main   
# ---------------------------------------------------------------------------    
if __name__ == '__main__':

    if sys.version_info < (3, 10):
        sys.exit("Please use Python 3.10+")
    
    with open('Feed.csv', newline='') as f:
        reader = csv.reader(f)
        RssFeedList = list(reader)
            
    for RssItem in RssFeedList:
        GetRssFromUrl(RssItem)
        CreateLogString(RssItem[1])

    GetRansomwareUpdates()
    CreateLogString("Ransomware List")

