import feedparser
import time
from configparser import ConfigParser
import requests
import urllib.request, json
import os #for github action 

ConfigurationFilePath = "./Config.txt" ##path to configuration file

FileConfig = ConfigParser()
FileConfig.read(ConfigurationFilePath)

# For Github action 
Url=os.getenv('MSTEAMS_WEBHOOK')

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
            Title = "🏴‍☠️ 🔒 "           
            Title += Entries["post_title"] 
            send_teams(Url,OutputMessage,Title)
            time.sleep(3)

            FileConfig.set('main', Entries["group_name"], Entries["discovered"])

    with open(ConfigurationFilePath, 'w') as FileHandle:
        FileConfig.write(FileHandle)

def FnGetRssFromUrl(RssItem, HookChannelDesciptor):
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
        Title = '📢 '
        Title += RssItem[1]
        send_teams(Url,OutputMessage,Title)
        time.sleep(3)

    with open(ConfigurationFilePath, 'w') as FileHandle:
        FileConfig.write(FileHandle)

    IsInitialRun = False

def FnCreateLogString(RssItem):
    LogString = "[*]" + time.ctime()
    LogString += " " + "checked " + RssItem
    print(LogString)
    time.sleep(2) 
    
def EntryMain():

    LogString = ""
    RssFeedList = [["https://grahamcluley.com/feed/", "Graham Cluley"],
                   ["https://threatpost.com/feed/", "Threatpost"],
                   ["https://krebsonsecurity.com/feed/", "Krebs on Security"],
                   ["https://www.darkreading.com/rss.xml", "Dark Reading"],
                   ["http://feeds.feedburner.com/eset/blog", "We Live Security"],
                   ["https://davinciforensics.co.za/cybersecurity/feed/", "DaVinci Forensics"],
                   ["https://blogs.cisco.com/security/feed", "Cisco"],
                   ["https://www.infosecurity-magazine.com/rss/news/", "Information Security Magazine"],
                   ["http://feeds.feedburner.com/GoogleOnlineSecurityBlog", "Google"],
                   ["http://feeds.trendmicro.com/TrendMicroResearch", "Trend Micro"],
                   ["https://www.bleepingcomputer.com/feed/", "Bleeping Computer"],
                   ["https://www.proofpoint.com/us/rss.xml", "Proof Point"],
                   ["http://feeds.feedburner.com/TheHackersNews?format=xml", "Hacker News"],
                   ["https://www.schneier.com/feed/atom/", "Schneier on Security"],
                   ["https://www.binarydefense.com/feed/", "Binary Defense"],
                   ["https://securelist.com/feed/", "Securelist"],
                   ["https://research.checkpoint.com/feed/", "Checkpoint Research"],
                   ["https://www.virusbulletin.com/rss", "VirusBulletin"],
                   ["https://modexp.wordpress.com/feed/", "Modexp"],
                   ["https://www.tiraniddo.dev/feeds/posts/default", "James Forshaw"],
                   ["https://blog.xpnsec.com/rss.xml", "Adam Chester"],
                   ["https://msrc-blog.microsoft.com/feed/", "Microsoft Security"],
                   ["https://www.recordedfuture.com/feed", "Recorded Future"],
                   ["https://www.sentinelone.com/feed/", "SentinelOne"],
                   ["https://redcanary.com/feed/", "RedCanary"],
                   ["https://cyber-news.fr/feeds/c/main.xml?sort=New", "Cyber-News"],
                   ["https://leak-lookup.com/rss","Leak-Lookup"]]
                   

    GovRssFeedList = [["https://www.cisa.gov/uscert/ncas/alerts.xml", "US-CERT CISA"],
                      ["https://www.ncsc.gov.uk/api/1/services/v1/report-rss-feed.xml", "NCSC"],
                      ["https://www.cisecurity.org/feed/advisories", "Center of Internet Security"],
                      ["https://cert.ssi.gouv.fr/alerte/feed/", "FR-CERT Alertes"],
                      ["https://cert.ssi.gouv.fr/avis/feed/", "FR-CERT Avis"],
                      ["https://www.enisa.europa.eu/publications/RSS", "EU-ENISA Publications"]
                      ]
            
    for RssItem in RssFeedList:
        FnGetRssFromUrl(RssItem, 1)
        FnCreateLogString(RssItem[1])

    for GovRssItem in GovRssFeedList:
        FnGetRssFromUrl(GovRssItem, 2)
        FnCreateLogString(GovRssItem[1])

    FnGetRansomwareUpdates()
    FnCreateLogString("Ransomware List")

                      
EntryMain()
