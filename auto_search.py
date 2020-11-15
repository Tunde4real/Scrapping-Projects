# -- coding: utf-8 -
# Written by Ibrahim Aderinto

'''
This script is for scraping tweets from twitter search results given some keywords for searching.
'''

import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def chrome(mode):
    '''A function to instantiate chrome driver

    pre: mode, representing either headless (preferred) or browser mode.
    post: the driver instantiated.
    '''

    from selenium.webdriver.chrome.options import Options

    if mode == 'h':
            #  Headless mode
        chrome_option = Options()
        chrome_option.add_argument("--headless")
        chrome_option.add_argument("--log-level=3")
        driver = webdriver.Chrome(options=chrome_option)

    elif mode == 'b':
        # Browser mode
        driver = webdriver.Chrome()

    else:
        print("Mode is invalid")
        return None

    return driver


class result:

    def __init__(self, section):
        self.section = section.find_element(By.XPATH, "div/div/article/div/div/div/div[2]/div[2]")

    def get_text(self):
        text = self.section.find_element(By.XPATH, "div[2]/div/div").text
        return re.sub('\n', ' ', text)
    
    def get_poster_handle(self):
        return self.section.find_element(By.XPATH, "div/div/div/div/div/a").get_attribute('href')[20:]
    
    def get_poster(self):
        return self.section.find_element(By.XPATH, "div/div/div/div/div/a/div/div/div/span/span").text
    
    def date_created(self):
        return self.section.find_element(By.XPATH, "div/div/div/div/a/time").get_attribute("datetime")


class page:

    def __init__(self, driver, keyword):
        self.driver = driver
        self.keyword = keyword
        self.tweets = []
        print(f"Scraping for {keyword}"+ '\n')

    def click_latest(self):
        self.driver.find_element(By.XPATH, "//body/div/div/div/div[2]/main/div/div/div/div/div/div/div[2]/nav/div/div[2]/div/div[2]/a").click()
        time.sleep(5)
    
    def search(self):
        self.driver.find_element(By.XPATH, "//body/div/div/div/div[2]/main/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/form/div/div/div/div[2]/input").clear()
        self.driver.find_element(By.XPATH, "//body/div/div/div/div[2]/main/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/form/div/div/div/div[2]/input").send_keys(self.keyword+"\n")
        time.sleep(5)
        self.click_latest()

    def scroll_down(self):
        month_now = datetime.now().month
        if month_now == 1:
            month_now = 12
        else:
            month_now -= 1

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            all_tweets = self.driver.find_elements(By.XPATH, "//body/div/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/section/div/div/div")
            
            tweet_month = 0
            for tweet in all_tweets:
                try:
                    tweet = result(tweet)
                    tweet_month = datetime.strptime(tweet.date_created()[:10], '%Y-%m-%d').month
                    if tweet_month == month_now:
                        self.tweets += [(tweet.get_text() + '\n')]
                except:
                    continue
            if tweet_month<month_now:
                break
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(3)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        time.sleep(5)
        self.tweets = set(self.tweets)
    
    def get_tweets(self):
        return self.tweets

    def get_driver(self):
        return self.driver


def main():
    driver = chrome('h')
    with open('data_file.csv') as f:
        keywords = [i[:-2].replace(',', ' ').strip() for i in f.readlines()][1:]
    
    driver.get("https://twitter.com/explore")
    driver.delete_all_cookies()
    time.sleep(2)

    for key in keywords:
        result_writer = open(key+'.csv', 'w', encoding='utf-8')
        result_writer.write('Tweets' + '\n')

        session = page(driver, key)
        session.search()
        session.scroll_down()
        tweets = session.get_tweets()

        for tweet in tweets:
            result_writer.write(tweet)
    
    driver.close()


if __name__=="__main__":
    main()

