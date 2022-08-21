#!/usr/bin/env python3  
# -*- coding: utf-8 -*- 
#----------------------------------------------------------------------------
# Created By  : Julien Mousqueton @JMousqueton
# Original By : VX-Underground 
# Created Date: 22/08/2022
# Version     : 2.1.1
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Imports 
# ---------------------------------------------------------------------------
import feedparser
import time, requests
import csv # Feed.csv
import sys # Python version 
import json # Ransomware feed via ransomwatch 
from configparser import ConfigParser
import os # Webhook OS Variable and Github action 
from os.path import exists
from optparse import OptionParser
import urllib.request
#from urllib.parse import urlparse
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

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

        if options.Debug:
            print(Title + " / "  + Entries["discovered"])
        else:
            Send_Teams(Url,OutputMessage,Title)
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

        if RssItem[1] == "VERSION":
                Title ='🔥 A NEW VERSION IS AVAILABLE : ' + RssObject.title
       
        if options.Debug:
            print(Title)
        else:
            Send_Teams(Url,OutputMessage,Title)
            time.sleep(3)

    with open(ConfigurationFilePath, 'w') as FileHandle:
        FileConfig.write(FileHandle)


# ---------------------------------------------------------------------------
# Function fetch Red Flag domains 
# ---------------------------------------------------------------------------
def GetRedFlagDomains():
    now = datetime.now()
    format = "%Y-%m-%d"
    today = now.strftime(format)
    yesterday = now - timedelta(days=1)
    yesterday = yesterday.strftime(format)

    try:
        TmpObject = FileConfig.get('main',"redflagdomains")
    except:
        FileConfig.set('main', "redflagdomains", str(yesterday))
        TmpObject = str(yesterday)

    TmpObject = datetime.strptime(TmpObject, '%Y-%m-%d')
    today = datetime.strptime(today, '%Y-%m-%d')

    today = today.date()
    TmpObject = TmpObject.date()

    if(TmpObject < today):
        FileConfig.set('main', "redflagdomains", str(today))
        url="https://red.flag.domains/posts/"+ str(today) + "/"
        try:
            response = urllib.request.urlopen(url)
            soup = BeautifulSoup(response, 
                                'html.parser', 
                                from_encoding=response.info().get_param('charset'))
            response_status = response.status
            if soup.findAll("meta", property="og:description"):
                OutputMessage = soup.find("meta", property="og:description")["content"][4:].replace('[','').replace(']','')
                Title = "🚩 Red Flag Domains créés ce jour (" +  str(today) + ")"
                if options.Debug:
                    print(Title)
                else:
                    Send_Teams(Url,OutputMessage.replace('\n','<br>'),Title)
                    time.sleep(3)
        except HTTPError as error:
            response_status = error.code
            pass 
    with open(ConfigurationFilePath, 'w') as FileHandle:
        FileConfig.write(FileHandle)


# ---------------------------------------------------------------------------
# Log  
# ---------------------------------------------------------------------------
def CreateLogString(RssItem):
    LogString = "[*]" + time.ctime()
    LogString += " " + "checked " + RssItem
    if not options.Quiet: 
        print(LogString)
    time.sleep(2) 


# ---------------------------------------------------------------------------
# Main   
# ---------------------------------------------------------------------------    
if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options]",
                          version="%prog 2.1.1")
    parser.add_option("-q", "--quiet",
                      action="store_true",
                      dest="Quiet",
                      default=False,
                      help="Quiet mode")
    parser.add_option("-D", "--debug",
                      action="store_true", 
                      dest="Debug",
                      default=False,
                      help="Debug mode : only output on screen nothing send to MS Teams",)
    parser.add_option("-d", "--domain",
                      action="store_true", 
                      dest="Domains",
                      default=False,
                      help="Enable Red Flag Domains source",)
    (options, args) = parser.parse_args()

    # Get Microsoft Teams Webhook from Github Action CI:Env.  
    Url=os.getenv('MSTEAMS_WEBHOOK')

    # Make some simple checks before starting 
    if sys.version_info < (3, 10):
        sys.exit("Please use Python 3.10+")
    #if (str(Url) == "None" and options.Debug == 'False'):
    if (str(Url) == "None" and not options.Debug):
             sys.exit("Please use a MSTEAMS_WEBHOOK variable")
    if not exists("./Config.txt"):
        sys.exit("Please add a Config.txt file")
    if not exists("./Feed.csv"):
        sys.exit("Please add the Feed.cvs file")
    
    # Read the Config.txt file   
    ConfigurationFilePath = "./Config.txt" ##path to configuration file
    FileConfig = ConfigParser()
    FileConfig.read(ConfigurationFilePath)

    with open('Feed.csv', newline='') as f:
        reader = csv.reader(f)
        RssFeedList = list(reader)
            
    for RssItem in RssFeedList:
        GetRssFromUrl(RssItem)
        CreateLogString(RssItem[1])

    GetRansomwareUpdates()
    CreateLogString("Ransomware List")
    
    if options.Domains: 
        GetRedFlagDomains()
        CreateLogString("Red Flag Domain")