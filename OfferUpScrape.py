# -*- coding: utf-8 -*-
# written by Ibrahim Aderinto

# import system module
import re
import sys
import time
import json
import random
from datetime import datetime

# import third party modules
import gspread
import pandas as pd
from IPython.display import clear_output
from extension import proxies
from df2gspread import df2gspread as d2g
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


""" Module Documentation: Scrapes products from OfferUp
"""

def chrome(mode='h') -> object:
    '''A function to instantiate chrome driver

        :arguments: 
            mode: representing either headless (preferred) or browser mode.

        :returns: 
            driver: the driver instantiated.
    '''
    username = 'deleted'
    password = 'deleted'
    endpoint = 'gate.smartproxy.com'
    port = '7000'
    chrome_options = Options()
    # bypass OS security
    chrome_options.add_argument('--no-sandbox')
    # overcome limited resources
    chrome_options.add_argument('--disable-dev-shm-usage')
    # disable chrome notifications
    chrome_options.add_argument("--disable-notifications")
    # don't tell chrome that it is automated
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])

    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36")
    chrome_options.add_argument("disable-infobars")
    # set download path
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
        "download.directory_upgrade": True,
        "useAutomationExtension": False
    }
    chrome_options.add_experimental_option("prefs", prefs)
    proxies_extension = proxies(username, password, endpoint, port)

    chrome_options.add_extension(proxies_extension)
    
    # instantiate a non-headless browser
    if mode=='b':
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.maximize_window()
        return driver
    
    # instantiate a headless browser
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920,1080)
    return driver


def get_credentials():
    '''
        A fucntion that returns credentials object that can be used to authenticate a
        google client. A google client is an object that has access to certain resources
        of the account who owns the credentials.

        arguments:
            None

        returns:
            credentials -  a credentials object.
    '''
    scope = [\
            "https://spreadsheets.google.com/feeds",
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
    ]

    key_file = {
        "type": "deleted",
        "project_id": "deleted",
        "private_key_id": "deleted",
        "private_key": "deleted",
        "client_email": "deleted",
        "client_id": "deleted",
        "auth_uri": "deleted",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "deleted"
    }

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(key_file, scopes=scope)
    return credentials


def get_parameters(google_client):
    '''
        A function to access the google spread sheet storing the parameters needed
        to run the bot and return them. The parameters are search keyword, limit
        (of products to be scraped), search radius, sort_option and zip codes.

        arguments:
            google_client - an authenticated google client.

        returns:
            parameters - a dictionary storing all parameters other than the zip codes.
            zip_codes - a list of all zip codes.
    '''
    # open specification sheet and get needed values
    spec_sheet = google_client.open("Specifications").sheet1
    spec_sheet = spec_sheet.get_all_values()
    limit, keyword, radius, sort_option = spec_sheet[1]
    limit = int(limit)

    # open zip code sheets and get needed values
    zip_sheet = google_client.open("Zip Codes").sheet1
    zip_sheet = zip_sheet.get_all_values()
    zip_codes = [i[-1] for i in zip_sheet[1:]]

    return {'limit':limit, 'search_keyword':keyword, 'search_radius':radius, 'sort_option':sort_option}, zip_codes


def parse_url(parameters):
    '''
        A method to contruct the full api url to access offerup

        arguments:
            parameters - a dict object that includes the parameters to be added to the
                         base_url. It includes values for limit, zipcode, page, search_keyword
                         and search_radius.

        returns:
            base_url - a string of the parsed url
    '''
    base_url = 'https://offerup.com/api/search/v4/feed?'
    base_url += f"limit={parameters['limit']}" + f"&q={parameters['search_keyword']}"
    base_url += f"&zipcode={parameters['zip_code']}" + f"&radius={parameters['search_radius']}"
    sort_option = ''
    if 'default(nearest first)' == parameters['sort_option']:
        return base_url
    elif 'price: low to high' == parameters['sort_option']:
        sort_option = 'price'
    elif 'price: high to low' == parameters['sort_option']:
        sort_option = '-price'
    base_url += f"&sort={sort_option}"
    return base_url


def transform(data):
    '''
        A function that transforms the search result data on the page into a suitable format

        arguments:
            data - a string of all the text on the page

        returns:
            items - a list of lists where each member list represents the
                    details of a product.
    '''
    data = json.loads(data)
    product_items = data['data']['feed_items']
    products = []
    for item in product_items:
        try:
            item = item['item']
            if bool(item['paid'])==True:
                continue
            date_posted = item['post_date']
            date_posted = date_posted.replace('T', ' ')
            date_posted = date_posted.replace('Z', '')
            image_link = item['photos'][0]['images']['detail']['url']
            image = f"=IMAGE(\"{image_link}\", 4, 60, 60)"
            title = item['title']
            price = float(item['price'])
            location = item['location_name']
            product_link = item['get_full_url']
            products += [[image, title, price, location, image_link, product_link, date_posted]]
        except:
            continue
    return products


def load_data(google_client, df):
    '''
        A method to write data into online google sheet.

        arguments:
            google_client - an authenticated google client.
            df - a dataframe containing the data to be written into the online sheet.

        returns:
            None
    '''

    spreadsheet_key = '12XIAXMmNNKsZExRkdAOEKbsXDX5Rl2rZNvQvHv7WgWM'
    wks_name = 'Sheet1' # worksheet name just in case you have multiple worksheets
    credentials = get_credentials()

    # upload df to spreadsheet, that is save data scrapped to spreadsheet.
    d2g.upload(df, spreadsheet_key, wks_name, credentials=credentials, row_names=False)
    time.sleep(5)

    # To solve the problem of incorrectly formatted image links formula
    sheet = google_client.open("OfferUpScrape").sheet1
    data = sheet.get_all_records()  # Get all data as a list of dictionaries, where each dictionary represents a row
    l = len(data)
    cell_list = sheet.range(f'A1:A{l}')
    sheet.update_cells(cell_list, value_input_option='USER_ENTERED')    # update all rows of first cell
    sheet.update('A1', 'Image', value_input_option='USER_ENTERED')  #update cell title
    print('Successfully uploaded data to Google Sheet')


def main(driver):
    '''
        The main function

        arguments:
            driver - an instantiated chrome webdriver object

        returns:
            None
    '''
    credentials = get_credentials()
    google_client = gspread.authorize(credentials)
    parameters, zip_codes = get_parameters(google_client)
    random.shuffle(zip_codes)

    all_products = []
    for code in zip_codes:
        # print(f'Scraping for zipcode {code}')
        parameters['zip_code'] = code
        url = parse_url(parameters)

        wait_time = 0
        while True:
          driver.get(url)
          time.sleep(wait_time)
          page_data = driver.find_element(By.TAG_NAME, 'body').text
          if page_data.strip() != '' or wait_time==20:
              break
          wait_time += 2
        time.sleep(10)
        print(page_data)

        products = transform(page_data)
        all_products += products
        time.sleep(2)

    df = pd.DataFrame(all_products, columns=['Image', 'Title', 'Price', 'Location', 'Image Link', 'Product Link', 'Date Posted'])
    df['Date Posted'] = pd.to_datetime(df['Date Posted'])

    # sort the data
    if parameters['sort_option'] == 'default(nearest first)':
        df = df.sort_values(by='Date Posted', ascending=False)
    elif parameters['sort_option'] == 'price: high to low':
        df = df.sort_values(by='Price', ascending=False)
    elif parameters['sort_option'] == 'price: low to high':
        df = df.sort_values(by='Price', ascending=True)

    df = df.drop_duplicates()
    load_data(google_client, df)


if __name__=="__main__":
    driver = chrome('b')
    main(driver)
