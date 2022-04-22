import sqlite3
import feedparser
import tweepy
from pyvirtualdisplay import Display
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from auth import (consumer_key, consumer_secret, access_token, access_token_secret)

def getRss(twitterApi):
    rssFeeds = { "#UKRun #UKRace #Running #RunChat #5k" : "https://rss.app/feeds/jQpuiIuSLzo5uqOA.xml",
               "#UKRun #UKRace #Running #RunChat #10k" : "https://rss.app/feeds/LDekrzpK19mo4fJH.xml",
               "#UKRun #UKRace #Running #RunChat #halfmarathon" : "https://rss.app/feeds/LDekrzpK19mo4fJH.xml",
               "#UKRun #UKRace #Running #RunChat #marathon" : "https://rss.app/feeds/bPeWWhxhQrX7deRc.xml",
               "#UKRun #UKRace #Running #RunChat #ultramarathon" : "https://rss.app/feeds/BtpOpAFSdcRRBvkU.xml",
               "#UKRun #UKRace #Running #RunChat #10m" : "https://rss.app/feeds/6lzgWkrc9168QruP.xml"}
    driverPath = ChromeDriverManager().install()
    service = webdriver.chrome.service(driverPath)
    options = webdriver.chrome.options()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    browser = webdriver.Chrome(service=service, options=options)
    for postType in rssFeeds:
        url = rssFeeds[postType]
        rssFeed = feedparser.parse(url)
        if rssFeed:
            for item in rssFeed["items"]:
                url = item["link"]
                blogTitle = item["title"].replace(" | Book @ Findarace", "")
                display = Display(visible=0, size=(800, 800))
                display.start()
                browser.get(url)
                time.sleep(15)
                link = browser.current_url
                if checkLink(link):
                    print("Already posted:", link)
                else:
                    twitterLengthTitle = (blogTitle[:160] + '...') if len(blogTitle) > 160 else blogTitle
                    message = postType + " " + twitterLengthTitle + " : " + link
                    saveLink(link)
                    print("Posted:", link)
                    twitterApi.update_status(message)
        else:
            print("Nothing found in feed", rssFeed)
    browser.quit()

def checkLink(link):
    conn = sqlite3.connect('rssFeed.sqlite')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS feed (link VARCHAR(100), UNIQUE(link));')
    cur.execute("SELECT link FROM feed WHERE link = ?;", (link,) )
    result = cur.fetchone()
    conn.commit()
    conn.close()
    if result is not None:
        return True
    return False

def saveLink(link):
    conn = sqlite3.connect('rssFeed.sqlite')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO feed (link) values (?);", (link,))
    conn.commit()
    conn.close()

def getTwitter():
    authenticationToken = tweepy.OAuthHandler(consumer_key,consumer_secret)
    authenticationToken.set_access_token(access_token,access_token_secret)
    twitter = tweepy.API(authenticationToken)
    return twitter

if __name__ == '__main__':
    twitterApi = getTwitter()
    getRss(twitterApi)