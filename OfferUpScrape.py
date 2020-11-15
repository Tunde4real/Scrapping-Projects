# -- coding: utf-8 -
# Written by Ibrahim Aderinto; contact @ ib4real914@gmail.com

from selenium import webdriver
import psycopg2, time, datetime, csv, pandas as pd


def chrome():
    ''' Fucntion for browsing with chrome '''

    from selenium.webdriver.chrome.options import Options
    #       Headless mode
    # chrome_option = Options()
    # chrome_option.add_argument("--headless")
    # driver = webdriver.Chrome(options=chrome_option)

    # Browser mode
    driver = webdriver.Chrome()

    return driver


def firefox():
    ''' Fucntion for browsing with firefox '''

    from selenium.webdriver.firefox.options import Options
    #       Headless mode
    # firefox_options  = Options()
    # firefox_options.add_argument('-headless')
    # driver = webdriver.Firefox(options=firefox_options,
    #                               executable_path=r'C:\Users\ib4re\Desktop\Desktop Folders\Orlando\geckodriver.exe')

    # Browser mode
    try:
        driver = webdriver.Firefox()
    except:
        print('webdriver for firefox not installed')

    return driver


def edge():
    ''' Fucntion for browsing with Microsoft edge '''

    from selenium.webdriver.edge.options import Options
    #       Headless mode
    # edge_options = Options()
    # edge_options.add_argument('--headless')
    # driver = webdriver.Edge(options=edge_options, 
    #                           executable_path=r'C:\Users\ib4re\Desktop\Desktop Folders\Orlando\edgedriver_win64\msedgedriver.exe')

    # Browser mode
    try:
        driver = webdriver.Edge()
    except:
        print("webdriver for Microsoft Edge not installed")

    return driver


def tear(address, browser):
    # Defining output lists
    names, prices, locations, imgs, urls= [], [], [], [], []

    browser = browser.lower()
    # Accessing the page
    if browser == 'chrome':
        driver = chrome()
    elif browser == 'firefox':
        driver = firefox()
    elif browser == 'edge':
        driver == edge()

    driver.get(address)
    time.sleep(20) # The program sleeps for 20 secs to allow all search results load

    lenght_div = len(list(driver.find_elements_by_xpath("//div[@id='db-item-list']/div")))
    
    x = 1
    while lenght_div >= x:
        lenght_a = len(list(driver.find_elements_by_xpath("//div[@id='db-item-list']/div[{}]/a".format(x))))

        y = 1
        while lenght_a >= y:
            img_tag = driver.find_element_by_xpath("//div[@id='db-item-list']/div[{}]/a[{}]/div/div/div/img".format(x, y))
            img_src = img_tag.get_attribute("data-src")
            
            name_tag = driver.find_element_by_xpath("//div[@id='db-item-list']/div[{}]/a[{}]/div/div[2]/span".format(x, y))
            name = name_tag.text

            loc_tag = driver.find_element_by_xpath("//div[@id='db-item-list']/div[{}]/a[{}]/div/div[2]/span[2]".format(x, y))
            loc = loc_tag.text

            price_tag = driver.find_element_by_xpath("//div[@id='db-item-list']/div[{}]/a[{}]/div/div[2]/div/span".format(x, y))
            price = price_tag.text

            a_tag = driver.find_element_by_xpath("//div[@id='db-item-list']/div[{}]/a[{}]".format(x, y))
            url = a_tag.get_attribute("href")

            prices.append(price)
            names.append(name)
            locations.append(loc)
            imgs.append(img_src)
            urls.append(url)

            y += 1
        
        x += 1

    driver.close()
    return names, prices, locations, imgs, urls


def write_database(names, prices, locations, imgs, urls, user, instance):
    timestamp = str(datetime.datetime.today())
    
    try:
        connection = psycopg2.connect(user = "godwiclg",
                                    password = "MbsfkOnYP8O6Su4hr3Kf6OS9rpKyVN6t",
                                    host = "ruby.db.elephantsql.com",
                                    port = "5432",
                                    database = "godwiclg")

        cursor = connection.cursor()

        data_url_query = '''SELECT url FROM Results'''
        cursor.execute(data_url_query)
        data_url = cursor.fetchall()

        db_urls = [urldb[0] for urldb in data_url]

        x = 0
        for url in urls:
            if url in db_urls:
                update_query = '''UPDATE INTO Results WHERE url = '%s' SET price = '%s', 
                                    description = '%s', location = '%s', image_Url = '%s',
                                    time_last_scraped = '%s', user_instance_time_last_scraped = '%s'
                                    '''%(url, prices[x], names[x], locations[x], imgs[x],
                                    timestamp, user+' '+instance+' '+timestamp)
                cursor.execute(update_query)
                connection.commit()
            else:
                update_query = '''INSERT INTO Results VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s') 
                                    '''%(names[x], prices[x], locations[x], urls[x], imgs[x], timestamp, timestamp, user+' '+instance+' '+timestamp)
                cursor.execute(update_query)
                connection.commit()
                print(names[x], prices[x], locations[x], urls[x], imgs[x], user+' '+instance+' '+timestamp, timestamp)
            x += 1

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
            if(connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")


def main():
    # Reading inputs from sample input.csv
    input_df = pd.read_csv('sample input.csv')
    user = str(list(input_df['User']))[2:-2]
    instance = str(list(input_df['Instance']))[1:-1]
    interval = str(list(input_df['Interval']))[1:-1]
    browser = str(list(input_df['Browser']))[2:-2]
    url = str(list(input_df['Address']))[2:-2]

    results = tear(url, browser)
    names, prices, locations, imgs, urls = results[0], results[1], results[2], results[3], results[4]
    write_database(names, prices, locations, imgs, urls, user, instance)

    return interval

if __name__ == "__main__":
    z = 1
    while True:
        interval = main()
        print("Done with scrape {} \n".format(z))
        time.sleep(int(str(interval)))
        z+=1
