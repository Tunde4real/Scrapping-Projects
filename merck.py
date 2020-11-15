# -- coding: utf-8 -
# Written by Ibrahim Aderinto

'''
This script is for scrapping all products' details from Merck (sigmaaldrich.com). It works by scraping products of
individual categories whose links and herein. The categories differ from each other and so their extraction is 
seperate.
'''


import re
import csv
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

products_category_links = {
                            'Analytical' : 'https://www.sigmaaldrich.com/analytical-chromatography/analytical-chromatography-catalog.html',
                            'Biology' : 'https://www.sigmaaldrich.com/life-science/life-science-catalog.html',
                            'Chemistry' : 'https://www.sigmaaldrich.com/chemistry/chemical-synthesis/chemical-synthesis-catalog.html',
                            'Material Science' : 'https://www.sigmaaldrich.com/materials-science/material-science-products.html',
                            'Pharma and Biopharma' : 'https://www.sigmaaldrich.com/safc.html',
                            'Labware' : 'https://www.sigmaaldrich.com/labware/labware-catalog.html',
                            }

# In case some products have been scrapped before. This is to ensure no product is added twice.
df = pd.read_csv('merck.csv', encoding='utf-8', delimiter=';', error_bad_lines=False)
df_product = list(df['Id'])

merck_csv = open('merck.csv', 'a', encoding='utf-8', newline='')
merck_writer = csv.writer(merck_csv, delimiter=';')
link_last_ind = 0
new_links = []
all_links = []


def firefox(mode):
    '''A function to instantiate firefox driver

    pre: mode, representing either headless (preferred) or browser mode.
    post: the driver instantiated.
    '''
    from selenium.webdriver.firefox.options import Options

    if mode == 'headless':
        #   Headless Mode
        firefox_options  = Options()
        firefox_options.add_argument('-headless')
        driver = webdriver.Firefox(options=firefox_options,
                                    executable_path=r'C:\Users\ib4re\Desktop\Desktop Folders\Erlend\geckodriver.exe')

    elif mode == 'browser':
        # Browser Mode
        driver = webdriver.Firefox()

    else:
        print("Mode is invalid")
        return None

    driver.get("https://www.sigmaaldrich.com")
    driver.find_element_by_xpath("//a[@title='Norway']").click()
    return driver


def chrome(mode):
    '''A function to instantiate chrome driver

    pre: mode, representing either headless (preferred) or browser mode.
    post: the driver instantiated.
    '''

    from selenium.webdriver.chrome.options import Options

    if mode == 'headless':
            #  Headless mode
        chrome_option = Options()
        chrome_option.add_argument("--headless")
        chrome_option.add_argument("--log-level=3")
        driver = webdriver.Chrome(options=chrome_option, executable_path=r'Your executable path')

    elif mode == 'browser':
        # Browser mode
        driver = webdriver.Chrome(executable_path=r'C:\Users\ib4re\Desktop\Desktop Folders\Erlend\chromedriver.exe')

    else:
        print("Mode is invalid")
        return None

    driver.get("https://www.sigmaaldrich.com")
    driver.find_element_by_xpath("//a[@title='Norway']").click()
    return driver


def get_links_bs4(source_html):
    '''A function to extract all links from a given source code
    
    pre: source code
    post: extracted links
    '''

    links = []
    soup = BeautifulSoup(str(source_html), 'lxml')
    a_tags = soup.find_all('a')

    for link in a_tags:
        links.append(link.get('href'))

    links = ['https://www.sigmaaldrich.com' + link for link in links]

    return links


def get_links(driver):
    '''A function to extract all links of a known category from a given page
    
    pre: driver object
    post: extracted links
    '''
    driver.find_element_by_xpath("//ul[@class='opcsectionlist']")
    products = []
    uls = driver.find_elements(By.XPATH, "//ul[@class='opcsectionlist']")

    for ul in uls:
        lis = ul.find_elements_by_tag_name("li")
        for li in lis:
            a_tag = li.find_element_by_tag_name("a")
            products += [a_tag.get_attribute('href')]
        
    return products


def get_products(driver):
    '''A function to extract products' names and ids from a given page
    
    pre: driver object
    post: None
    '''

    global df_product
    driver.find_element(By.XPATH, "//table[@class='opcTable']")
    tables = driver.find_elements(By.XPATH, "//table[@class='opcTable']")
    for table in tables:
        lenght = len(list(table.find_elements(By.XPATH, "tbody/tr")))
        heads = table.find_elements(By.XPATH, "thead/tr/th")
        z = 0
        for head in heads:
            z += 1
            if 'Description' in head.text or 'Product Name' in head.text:
                break
        x = 1
        while x <= lenght:
            product_id = table.find_element(By.XPATH, "tbody/tr[{}]/td/a".format(x)).text
            # product_link = table.find_element(By.XPATH, "//table[@class='opcTable']/tbody/tr[{}]/td/a".format(x)).get_attribute('href')
            product_desc = table.find_element(By.XPATH,"tbody/tr[{}]/td[{}]/a".format(x, z)).text
            x += 2
            if len(set([product_id]).intersection(set(df_product))) >= 1:
                continue
            else:
                print(product_id)
                merck_writer.writerow([product_desc, product_id])
                df_product += [product_id]
    return True


def tear(link, driver):
    '''Since pages either contain links or products' details to be extracted, this function does whichever of the
        two is needed.

    pre: a page link, driver object
    post: None
    '''

    driver.get(link)
    if 'Page=' not in link:
        return False
    try:
        products = get_products(driver)
        return products
    except:
        try:
           new_links = get_links(driver)
           return new_links
        except:
            return False


def analytical(driver):
    '''A function to extract products' details from analytical category

    pre: driver object
    post: None
    '''

    global link_last_ind
    global new_links
    global all_links

    driver.get(products_category_links['Analytical'])
    links = []

    a = driver.find_elements_by_xpath("//div[@class='parsys_column cq-colctrl-lt1']/div")
    for i in a:
        h = i.get_attribute('innerHTML')
        links += get_links_bs4(h)

    err_link1 = "https://www.sigmaaldrich.com/content/sigma-aldrich/global-home/global/en/analytical-chromatography/analytical-products.html?TablePage=8656364"
    del(links[-9])
    links.append(err_link1)

    while True:
        links = set(links)
        common_links = links.intersection(set(all_links))
        links = list(links.difference(common_links))
        for link in links:
            results = tear(link, driver)
            if results == True or results == False:
                continue
            else:
                new_links += results
            link_last_ind += 1
        print('\n', new_links, '\n')
        if len(new_links) == 0:
            break
        else:
            links = new_links
            link_last_ind = 0
            new_links = []


def biology(driver):
    '''A function to extract products' details from biology category

    pre: driver object
    post: None
    '''

    global link_last_ind
    global new_links
    global all_links

    driver.get(products_category_links['Biology'])
    links = []

    a = driver.find_elements_by_xpath("//div[@class='parsys_column cq-colctrl-lt1']/div")
    for i in a:
        h = i.get_attribute('innerHTML')
        links += get_links_bs4(h)

    links.remove('https://www.sigmaaldrich.com/analytical-chromatography/analytical-chromatography-catalog.html')
    links.remove('https://www.sigmaaldrich.com/labware/labware-catalog.html')

    link1 = 'https://www.sigmaaldrich.com/life-science/biochemicals/biochemical-products.html?TablePage=20964389'
    link2 = 'https://www.sigmaaldrich.com/life-science/biochemicals/biochemical-products.html?TablePage=15077099'
    link3 = 'https://www.sigmaaldrich.com/life-science/cell-biology/cell-biology-products.html?TablePage=9552557'
    link4 = 'https://www.sigmaaldrich.com/life-science/biochemicals/biochemical-products.html?TablePage=103955322'
    links += [link1, link2, link3, link4]

    if driver == 'get':
        return links

    while True:
        links = set(links)
        common_links = links.intersection(set(all_links))
        links = list(links.difference(common_links))
        for link in links:
            results = tear(link, driver)
            if results == True or results == False:
                continue
            else:
                new_links += results
            link_last_ind += 1
        print('\n', new_links, '\n')
        if len(new_links) == 0:
            break
        else:
            links = new_links
            link_last_ind = 0
            new_links = []


def chemistry(driver):
    '''A function to extract products' details from chemistry category

    pre: driver object
    post: None
    '''

    global link_last_ind
    global new_links
    global all_links

    driver.get(products_category_links['Chemistry'])
    links = []
    divs = driver.find_elements(By.XPATH, "//div[@class='rawhtml section']/table/tbody/tr")

    for element in divs:
        lenght = len(list(element.find_elements_by_tag_name("td")))
        x = 1
        while x <= lenght:
            try:
                a = element.find_element(By.XPATH, "td[{}]/a".format(x)).get_attribute('href')
            except:
                a = element.find_element(By.XPATH, "td[{}]/span/a".format(x)).get_attribute('href')
            links += [a]
            x += 2
    
    while True:
        links = set(links)
        common_links = links.intersection(set(all_links))
        links = list(links.difference(common_links))
        print(len(links))
        for link in links:
            if link == 'https://www.sigmaaldrich.com/chemistry/solvents.html' or link == 'https://www.sigmaaldrich.com/chemistry/stockroom-reagents.html':
                a = driver.find_elements_by_xpath("//div[@class='parsys_column cq-colctrl-lt1'][1]/div")
                for i in a:
                    h = i.get_attribute('innerHTML')
                    new_links += get_links_bs4(h)
            else:
                results = tear(link, driver)
                if results == True or results == False:
                    continue
                else:
                    new_links += results
        print('\n', new_links, '\n')
        if len(new_links) == 0:
            break
        else:
            links = new_links


def material_science(driver):
    '''A function to extract products' details from material science category

    pre: driver object
    post: None
    '''

    global link_last_ind
    global new_links
    global all_links

    driver.get(products_category_links['Material Science'])
    links = get_links(driver)
    
    while True:
        links = set(links)
        common_links = links.intersection(set(all_links))
        links = list(links.difference(common_links))
        for link in links:
            if link == 'https://www.sigmaaldrich.com/materials-science/polymer-science.html':
                a = driver.find_elements_by_xpath("//div[@class='parsys_column cq-colctrl-lt1'][1]/div")
                for i in a:
                    h = i.get_attribute('innerHTML')
                    new_links += get_links_bs4(h)
                continue
            results = tear(link, driver)
            if results == True or results == False:
                continue
            else:
                new_links += results
        print('\n', new_links, '\n')
        if len(new_links) == 0:
            break
        else:
            links = new_links


def labware(driver):
    '''A function to extract products' details from labware category

    pre: driver object
    post: None
    '''

    global link_last_ind
    global new_links
    global all_links

    driver.get(products_category_links['Labware'])
    tables = driver.find_elements(By.XPATH, "//div[@class='text parbase section']/table/tbody/tr/td")
    links = []

    for table in tables:
        lenght = len(list(table.find_elements(By.XPATH, "table/tbody/tr")))
        x = 1
        while x<=lenght:
            elem = table.find_element(By.XPATH, "table/tbody/tr[{}]/td[2]/a".format(x)).get_attribute('href')
            links += [elem]
            x+=1

    while True:
        links = set(links)
        common_links = links.intersection(set(all_links))
        links = list(links.difference(common_links))
        for link in links:
            results = tear(link, driver)
            if results == True or results == False:
                continue
            else:
                new_links += results
        print('\n', new_links, '\n')
        if len(new_links) == 0:
            break
        else:
            links = new_links



if __name__ == "__main__":
    try:
        driver = chrome('headless')
        analytical(driver)
        biology(driver)
        chemistry(driver)
        material_science(driver)
        labware(driver)
        driver.close()
        print('done')
    except:
        with open('stop_position.txt', 'w') as f:
            links = biology('get')
            links = links[link_last_ind:]
            links = new_links + links
            f.write(str(links))
        print("Encountered an error")
