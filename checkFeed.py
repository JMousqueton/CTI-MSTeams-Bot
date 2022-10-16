import urllib.request
import feedparser,csv

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

with open('Feed.csv', newline='') as f:
    reader = csv.reader(f)
    RssFeedList = list(reader)

for RssItem in RssFeedList:
    if '#' in str(RssItem[0]):
                continue
    Feed = feedparser.parse(RssItem[0])
    try:
        print("✅ " + color.BOLD + RssItem[1] + color.END + " ("+ Feed.entries[0].published + ")")
    except:
        try:
            print("✅ " + color.BOLD + RssItem[1] + color.END + " ("+ Feed.entries[0].updated + ")")
        except:
            print("❌ " + color.BOLD  + RssItem[1] +  color.END + color.RED + " RSS ERROR !" + color.END)