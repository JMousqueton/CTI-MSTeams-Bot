#!/usr/bin/env python3  
# -*- coding: utf-8 -*- 
#----------------------------------------------------------------------------
# Created By  : Julien Mousqueton @JMousqueton
# Original By : VX-Underground 
# Created Date: 22/08/2022
# Version     : 3.0.0 (2023-05-15)
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
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

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
# Fetch Ransomware attacks from https://www.ransomware.live 
# ---------------------------------------------------------------------------
def GetRansomwareUpdates():
    
    Data = requests.get("https://data.ransomware.live/posts.json")
        
    for Entries in Data.json():

        DateActivity = Entries["discovered"]
            
        # Correction for issue #1 : https://github.com/JMousqueton/CTI-MSTeams-Bot/issues/1
        try:
            TmpObject = FileConfig.get('Ransomware', Entries["group_name"])
        except:
            FileConfig.set('Ransomware', Entries["group_name"], " = ?")
            TmpObject = FileConfig.get('Ransomware', Entries["group_name"])

        if TmpObject.endswith("?"):
            FileConfig.set('Ransomware', Entries["group_name"], DateActivity)
        else:
            if(TmpObject >= DateActivity):
                continue
        #else:
        #    FileConfig.set('Ransomware', Entries["group_name"], Entries["discovered"])

        OutputMessage = "Group : <b>"
        OutputMessage += "<a href=\"https://www.ransomware.live/#/profiles?id="
        OutputMessage += Entries["group_name"]
        OutputMessage += "\">"
        OutputMessage += Entries["group_name"]
        OutputMessage += "</a>"
        OutputMessage += "</b><br>🗓 "
        OutputMessage += Entries["discovered"]
        OutputMessage += "</b><br>🗒️ "
        OutputMessage += Entries["description"]
        OutputMessage += "</b><br>🌍 <a href=\"https://www.google.com/search?q="
        OutputMessage += Entries["post_title"].replace("*.", "")
        OutputMessage += "\">"
        OutputMessage += Entries["post_title"]
        OutputMessage += "</a>"
        
        Title = "🏴‍☠️ 🔒 "     

        if Entries["post_title"].find(".fr") != -1:
            Title += " 🇫🇷 "

        Title += Entries["post_title"].replace("*.", "") 
        Title += " by "
        Title += Entries["group_name"]

        if options.Debug:
            print(Entries["group_name"] + " = " + Title + " ("  + Entries["discovered"]+")")
        else:
            Send_Teams(webhook_ransomware,OutputMessage,Title)
            time.sleep(3)

        FileConfig.set('Ransomware', Entries["group_name"], Entries["discovered"])

    with open(ConfigurationFilePath, 'w') as FileHandle:
        FileConfig.write(FileHandle)


# ---------------------------------------------------------------------------
# Add nice Emoji in front of title   
# ---------------------------------------------------------------------------
def Emoji(feed):
    # Nice emoji :) 
    match feed:
        case "Leak-Lookup":
            Title = '💧 '
        case "VERSION":
            Title = '🔥 '
        case "DataBreaches":
            Title = '🕳 '
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
        case "Cisco":
            Title = '📡 '
        case "Securelist":
            Title = '📜 '
        case "ATT":
            Title = '📞 '
        case "Google TAG":
            Title = '🔬 '
        case "DaVinci Forensics":
            Title = '📐 '
        case "VirusBulletin":
            Title = '🦠 '
        case "Information Security Magazine":
            Title = '🗞 '
        case "US-CERT CISA":
            Title = '🇺🇸 '
        case "NCSC":
            Title = '🇬🇧 '
        case "SANS":
            Title = '🌍 '
        case "malpedia":
            Title = '📖 '
        case "Unit42":
            Title = '🚓 '
        case "Microsoft Security":
            Title = 'Ⓜ️ '
        case "Checkpoint Research":
            Title = '🏁 '
        case "Proof Point":
            Title = '🧾 '
        case "RedCanary":
            Title = '🦆 '
        case "MSRC Security Update":
            Title = '🚨 '
        case "CIRCL Luxembourg":
            Title = '🇱🇺 '
        case _:
            Title = '📢 '
    return Title


# ---------------------------------------------------------------------------
# Function fetch RSS feeds  
# ---------------------------------------------------------------------------
def GetRssFromUrl(RssItem):
    NewsFeed = feedparser.parse(RssItem[0])
    DateActivity = ""
    IsInitialRun = False

    for RssObject in reversed(NewsFeed.entries):

        try:
            DateActivity = time.strftime('%Y-%m-%dT%H:%M:%S', RssObject.published_parsed)
        except: 
            DateActivity = time.strftime('%Y-%m-%dT%H:%M:%S', RssObject.updated_parsed)
        
        # Correction for issue #1 : https://github.com/JMousqueton/CTI-MSTeams-Bot/issues/1
        try:
            TmpObject = FileConfig.get('Rss', RssItem[1])
        except:
            FileConfig.set('Rss', RssItem[1], " = ?")
            TmpObject = FileConfig.get('Rss', RssItem[1])

        if TmpObject.endswith("?"):
            FileConfig.set('Rss', RssItem[1], DateActivity)
        else:
            if(TmpObject >= DateActivity):
                continue

        OutputMessage = "Date: " + DateActivity
        OutputMessage += "<br>"
        # OutputMessage += "Title:<b> " + RssObject.title
        OutputMessage += "Source:<b> " + RssItem[1]
        OutputMessage += "</b><br>"
        OutputMessage += "Read more: " + RssObject.link
        OutputMessage += "<br>"

        Title = Emoji(RssItem[1])
        Title += " " + RssObject.title

        if RssItem[1] == "VERSION":
                Title ='🔥 A NEW VERSION IS AVAILABLE : ' + RssObject.title
       
        if options.Debug:
            print(Title + " : " + RssObject.title + " (" + DateActivity + ")")
        else:
            Send_Teams(webhook_feed,OutputMessage,Title)
            time.sleep(3)
        
        FileConfig.set('Rss', RssItem[1], DateActivity)

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
        TmpObject = FileConfig.get('Misc',"redflagdomains")
    except:
        FileConfig.set('Misc', "redflagdomains", str(yesterday))
        TmpObject = str(yesterday)

    TmpObject = datetime.strptime(TmpObject, '%Y-%m-%d')
    today = datetime.strptime(today, '%Y-%m-%d')

    today = today.date()
    TmpObject = TmpObject.date()

    if(TmpObject < today):
        url="https://red.flag.domains/posts/"+ str(today) + "/"
        try:
            response = urllib.request.urlopen(url)
            soup = BeautifulSoup(response, 
                                'html.parser', 
                                from_encoding=response.info().get_param('charset'))
            # response_status = response.status
            #if soup.findAll("meta", property="og:description"):
            #    OutputMessage = soup.find("meta", property="og:description")["content"][4:].replace('.wf ','').replace('.yt ','').replace('.re ','').replace('[','').replace(']','')
            div = soup.find("div", {"class": "content", "itemprop": "articleBody"})
            for p in div.find_all("p"):
                OutputMessage = re.sub("[\[\]]", "", (p.get_text()))
            Title = "🚩 Red Flag Domains créés ce jour (" +  str(today) + ")"
            FileConfig.set('Misc', "redflagdomains", str(today))
            if options.Debug:
                print(Title)
                print(OutputMessage)
            else:
                Send_Teams(webhook_feed,OutputMessage.replace('\n','<br>'),Title)
                time.sleep(3)
        except:
            pass 
    with open(ConfigurationFilePath, 'w') as FileHandle:
        FileConfig.write(FileHandle)

# ---------------------------------------------------------------------------
# Function Send Feeds Reminder 
# ---------------------------------------------------------------------------
def SendReminder():
    now = datetime.now()
    format = "%Y-%m-%d"
    today = now.strftime(format)
    lastmonth = now - timedelta(days=31)
    lastmonth = lastmonth.strftime(format)
    try:
        TmpObject = FileConfig.get('Misc',"reminder")
    except:
        FileConfig.set('Misc', "reminder", str(lastmonth))
        TmpObject = str(lastmonth)
   
    TmpObject = datetime.strptime(TmpObject, '%Y-%m-%d')
    today = datetime.strptime(today, '%Y-%m-%d')
    lastmonth = datetime.strptime(lastmonth, '%Y-%m-%d')
    
    if(TmpObject < lastmonth):
        Title = "🤔 Monthly Feeds Reminder"
        if options.Debug:
            print(Title)
        OutputMessage="Feeds : "
        OutputMessage += "<br>"
        with open('Feed.csv', newline='') as f:
            reader = csv.reader(f)
            RssFeedList = list(reader)

        for RssItem in RssFeedList:
            if '#' in str(RssItem[0]):
                continue
            Feed = feedparser.parse(RssItem[0])
            try:
                OutputMessage += Emoji(RssItem[1]) + RssItem[1] + "  (" + Feed.entries[0].published + ")"
                OutputMessage += "<br>"
            except:
                try:
                    OutputMessage += Emoji(RssItem[1]) + RssItem[1] + "  (" + Feed.entries[0].updated + ")"
                    OutputMessage += "<br>"
                except:
                    continue
        if options.Domains: 
            OutputMessage += "Misc : "
            OutputMessage += "<br>"
            OutputMessage += "🚩 Red Flag Domains"
            OutputMessage += "<br>"
        OutputMessage += "Ransomware :"
        OutputMessage += "<br>"
        OutputMessage += "🏴‍☠️ 🔒 Ransomware Leaks"
        OutputMessage += "<br><br>"
        OutputMessage += "Coded with ❤️ by JMousqueton"
        OutputMessage += "<BR>"
        OutputMessage += "Code : https://github.com/JMousqueton/CTI-MSTeams-Bot"
        today = today.strftime(format)
        FileConfig.set('Misc', "reminder", str(today))
        if options.Debug:
            print(OutputMessage)
        else: 
            Send_Teams(Url,OutputMessage,Title)    

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
                          version="%prog 2.2.0")
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
    parser.add_option("-r", "--reminder",
                      action="store_true",
                      dest="Reminder",
                      default=False,
                      help="Enable monthly reminder of Feeds")
    (options, args) = parser.parse_args()

    # Get Microsoft Teams Webhook from Github Action CI:Env.  
    webhook_feed=os.getenv('MSTEAMS_WEBHOOK_FEED')
    webhook_ransomware=os.getenv('MSTEAMS_WEBHOOK_RANSOMWARE')
    webhook_ioc=os.getenv('MSTEAMS_WEBHOOK_IOC')

    # expects the configuration file in the same directory as this script by default, replace if desired otherwise
    ConfigurationFilePath = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'Config.txt')

    # Make some simple checks before starting 
    if sys.version_info < (3, 10):
        sys.exit("Please use Python 3.10+")
    if (str(webhook_feed) == "None" and not options.Debug):
             sys.exit("Please use a MSTEAMS_WEBHOOK_FEED variable")
    if (str(webhook_ransomware) == "None" and not options.Debug):
             sys.exit("Please use a MSTEAMS_WEBHOOK_RANSOMWARE variable")
    if (str(webhook_ioc) == "None" and not options.Debug):
             sys.exit("Please use a MSTEAMS_WEBHOOK_IOC variable")

    if not exists(ConfigurationFilePath):
        sys.exit("Please add a Config.txt file")
    if not exists("./Feed.csv"):
        sys.exit("Please add the Feed.cvs file")
    
    # Read the Config.txt file   
    # ConfigurationFilePath = "./Config.txt" ##path to configuration file
    FileConfig = ConfigParser()
    FileConfig.read(ConfigurationFilePath)

    with open('Feed.csv', newline='') as f:
        reader = csv.reader(f)
        RssFeedList = list(reader)
            
    for RssItem in RssFeedList:
        if '#' in str(RssItem[0]):
            continue
        GetRssFromUrl(RssItem)
        CreateLogString(RssItem[1])

    GetRansomwareUpdates()
    CreateLogString("Ransomware List")
    
    if options.Domains: 
        GetRedFlagDomains()
        CreateLogString("Red Flag Domains")

    if options.Reminder:
        SendReminder()
        CreateLogString("Reminder")
