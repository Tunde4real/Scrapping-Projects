'''This is a script that automates submission of book details to book promotion sites. It will automatically 
submit to 15 different sites.

Required dependencies:
1. python3
2. pandas
3. mechancial soup (python -m pip install mechanicalsoup --user)
4. selenium chrome driver
5. selenium framework (python -m pip install selenium --user)
'''

import datetime
import mechanicalsoup as ms
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

chrome_option = Options()
chrome_option.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_option)
#driver = webdriver.Chrome()

def find(name, value):
    element = driver.find_element_by_name(name)
    element.clear()
    element.send_keys(value)

data = pd.read_csv("dataset.csv")
lenght, x = len(data), 0


while x < lenght:
    amazon = data["Amazon Link"][x]
    ASIN = data["ASIN Number"][x]
    bio = data["Author's Bio"][x]
    email = data["Author's Email"][x]
    title = data["Author's Title"][x]
    name = data["Author's Name"][x]
    website = data["Author's Website"][x]
    book_on_kindle = data["Book on kindle? (Yes or No)"][x]
    book_category = data["Book's Category"][x]
    book_price = data["Book's Price (without currency sign)"][x]
    book_genre = data["Book's Genre"][x]
    pricing_status = data["Book's Pricing Status (free or priced?)"][x]
    start_date = data["Book's Promotion Start Date"][x]
    start = [int(i) for i in start_date.split()]
    syear, smonth, sday = start[0], start[1], start[2]
    end_date = data["Book's Promotion End Date"][x]
    end = [int(i) for i in end_date.split()]
    eyear, emonth, eday = end[0], end[1], end[2]
    book_sypnosis = data["Book Sypnosis"][x]
    book_tag = data["Book's Tag"][x]
    book_title = data["Book's Title"][x]
    cover_image = data["Cover Image Path"][x]
    blurb = data["Blurb"][x]
    paypal_email = data["Paypal Email"][x]
    state_of_residence = data["State of Residence"][x]
    twitter = data["Twitter Handle"][x]
    reviews = data["Reviews (in Number)"]


    def BookBongo():
        browser = ms.StatefulBrowser(
            soup_config={'features': 'lxml'},               # lxml is the best html parser available
            raise_on_404=True,                              # raise error on inability to connect
            )                                               # creating an instance of mechanical soup's stateful browser
        browser.open("https://bookbongo.com/submit/")
        # print(browser.get_current_page())                   # TO get the html of the current page
        browser.select_form('form[method="post"]')
        # form.print_summary()                                  # To print  out all the input elements in the form. You must set form = browser.select_form
        browser['radio-461'] = title
        browser["your-name"] = name
        browser["your-email"] = email
        browser["subscribed"] = "Subscribe me to the Book Bongo weekly mailout"
        browser["your-author"] = name
        browser["your-title"] = book_title
        browser["your-genre"] = book_genre
        browser["book-amazon"] = amazon
        browser["radio-490"] = pricing_status

        if pricing_status == "priced":
            browser["discount-price"] = book_price

        browser["date-promotion-start"] = datetime.date(syear, smonth, sday)
        browser["date-promotion-end"] = datetime.date(eyear, emonth, eday)
        browser["your-blurb"] = blurb
        browser.submit_selected()
        print("1. Successfully submitted book details to Book Bongo") 
        # browser.launch_browser()    

    def EBooksHabit():
        browser = ms.StatefulBrowser(
            soup_config={'features': 'lxml'},
            raise_on_404=True,
            )
        browser.open("http://ebookshabit.com/for-authors/")
        browser.select_form('form[method="post"]')
        browser["youremail"] = email
        browser["asin"] = ASIN
        browser["price"] = book_price
        browser["from"] = str(smonth) + '/' + str(sday) + '/' + str(syear)
        browser["to"] = str(emonth) + '/' + str(eday) + '/' + str(eyear)
        browser.submit_selected()
        print("2. Successfully submitted book details to ebooks habit") 

    def ItsWriteNow():
        browser = ms.StatefulBrowser(
            soup_config={'features': 'lxml'},
            raise_on_404=True,
            )
        browser.open("https://itswritenow.com/free-book-submission/")
        browser.select_form('form[method="post"]')
        browser["item_meta[108]"] = name
        browser["item_meta[10]"] = email
        browser["item_meta[109]"] = name
        browser["item_meta[138]"] = twitter
        browser["item_meta[9]"] = book_title
        browser["iten_meta[12]"] = ASIN
        browser["item_meta[16]"] = amazon
        browser["item_meta[351][]"] = book_category
        browser["item_meta[558]"] = book_tag

        if pricing_status == "free":
            book_free = "Yes"
        else:
            book_free = "No"

        browser["item_meta[21]"] = book_free

        if book_free == "No":
            browser["item_meta[828]"] = book_price
            browser["item_meta[829]"] = book_on_kindle
            browser["item_meta[106]"] = datetime.date(syear, smonth, sday)
            browser["item_meta[107]"] = datetime.date(eyear, emonth, eday)
        browser.submit_selected()
        print("3. Successfully submitted book details to It's write now") 

    def ZwoodleBooks():
        browser = ms.StatefulBrowser(
            soup_config={'features': 'lxml'},
            raise_on_404=True,
            )
        browser.open("http://zwoodlebooks.com/submissions/ ")
        browser.select_form('form[method="post"]')
        browser["g2-yourname"] = name
        browser["g2-youremail"] = email
        browser["g2-authorname"] = name
        browser["g2-twitterhandleex-zwoodlebooks"] = twitter
        browser["g2-booktitle"] = book_title
        browser["g2-genre"] = book_genre
        browser["g2-whereisthisbookofferedexclusivetokindleifnotpleaseincludeurlstowhereitisavailable"] = amazon
        browser["g2-ihavereadandagreetotheabovetermsandconditions"] = "Yes"
        browser.submit_selected()
        print("4. Successfully submitted book details to Zwoodle Books") 
    
    def LovelyBooks():
        browser = ms.StatefulBrowser(
            soup_config={'features': 'lxml'}
            )
        browser.open("https://fkbt.com/for-authors/free-kindle-promotion/")
        browser.select_form('form[method="post"]')
        browser["your-name"] = name
        browser["your-email"] = email
        browser["PayPalEmail"] = paypal_email
        browser["StateofResidence"] = state_of_residence
        browser["book-link"] = amazon
        browser["book-title"] = title
        browser["book-promo-price"] = book_price
        browser["book-genre"] = book_genre
        browser["date-1"] = str(datetime.date(syear, smonth, sday)) + '-' + str(datetime.date(eyear, emonth, eday))
        browser.submit_selected()
        print("5. Successfully submitted book details to Lovely Books") 

    def Freebie():
        browser = ms.StatefulBrowser(
            soup_config={'features': 'lxml'},
            raise_on_404=True,
            )
        browser.open("http://form.jotformpro.com/form/21078469493969")
        browser.select_form('form[method="post"]')
        browser["q4_authorsFull[first]"] = name.split()[0]
        browser["q4_authorsFull[last]"] = name.split()[1]
        browser["q5_contactEmail"] = email
        browser["q7_bookTitle"] = book_title
        browser["q8_amazonLink"] = amazon
        browser["q30_briefBlurb"] = blurb
        browser["q25_twitterHandle25"] = twitter
        browser["q9_day19[month]"] = smonth
        browser["q9_day19[day]"] = sday
        browser["q9_day19[year]"] = syear
        browser["q10_lastDay10[month]"] = emonth
        browser["q10_lastDay10[day]"] = eday
        browser["q10_lastDay10[year]"] = eyear
        browser["q14_paymentOptions[][id]"] = 1004
        browser.submit_selected()
        print("6. Successfully submitted book details to Freebie") 

    def AwesomeGang():
        driver.get("https://awesomegang.com/submit-your-book/")
        find('input_1', book_title)
        find('input_2', book_sypnosis)
        find('input_21', bio)
        find('input_17', cover_image)
        find('input_6', website)
        find('input_10', amazon)
        find('input_11', twitter)
        find('input_4', email)
        find('input_13', book_genre)
        find('input_16', '0' + str(smonth) +'/'+ str(sday) + '/'+ str(syear))
        driver.find_element_by_id('gform_submit_button_12').click()
        print("7. Successfully submitted book details to Awesome Gang") 


    def PreetyHot():
        driver.get("https://pretty-hot.com/submit-your-book/")
        names = ['input_1', 'input_2', 'input_8', 'input_6', 'input_10', 'input_11', 'input_9', 'input_4', 'input_17', 'input_13', 'input_16']
        values = [book_title, book_sypnosis, bio, website, amazon, twitter, cover_image, email, book_category, book_genre, '0' + str(smonth) +'/'+ str(sday) + '/'+ str(syear)]
        y = 0
        while y<len(names):
            if names[y] == 'input_17':
                select = Select(driver.find_element_by_name('input_17'))
                select.select_by_visible_text(values[y])
                y+=1
                continue
            find(names[y], values[y])
            y += 1
        driver.find_element_by_id('gform_submit_button_4').click()
        print("8. Successfully submitted book details to Preety Hot") 

    def FreeBooksy():
        driver.get("https://www.freebooksy.com/editorial-submissions/")
        driver.implicitly_wait(10) 
        names = ['item_meta[86]', 'item_meta[87]', 'item_meta[88]', 'item_meta[93]', 'item_meta[97]', 'item_meta[96]' ]
        values = [name.split()[0], name.split()[1], email, amazon, '0' + str(smonth) +'/'+ str(sday) + '/'+ str(syear), '0' + str(emonth) +'/'+ str(eday) + '/'+ str(eyear)]
        y = 0
        while y<len(names):
            find(names[y], values[y])
            y+=1
        driver.find_element(By.ID, "field_lg3nv8-0").click()
        driver.find_element(By.CSS_SELECTOR, ".frm_submit > input").click()
        print("9. Successfully submitted to Freebooksy")

    def EReader():
        driver.get("http://ereadergirl.com/submit-your-ebook/")
        driver.implicitly_wait(10)
        driver.find_element(By.ID, "input_1_1").send_keys(name)
        driver.find_element(By.ID, "input_1_3").send_keys(email)
        driver.find_element(By.ID, "input_1_4").click()
        dropdown = driver.find_element(By.ID, "input_1_4")
        dropdown.find_element(By.XPATH, "//option[. = 'Free']").click()
        driver.find_element(By.ID, "input_1_4").click()
        driver.find_element(By.ID, "input_1_5").send_keys(amazon)
        driver.find_element(By.ID, "input_1_6").send_keys(str(ASIN))
        driver.find_element(By.ID, "gform_submit_button_1").click()
        print("10. Successfully submitted to Ereader")
    

    def JotFormPro():
        driver.get("http://form.jotformpro.com/form/21078469493969")
        driver.implicitly_wait(10)
        driver.find_element(By.ID, "first_4").click()
        driver.find_element(By.ID, "first_4").send_keys(name.split()[0])
        driver.find_element(By.ID, "last_4").send_keys(name.split()[1])
        driver.find_element(By.ID, "input_5").send_keys(email)
        driver.find_element(By.ID, "input_7").send_keys(book_title)
        driver.find_element(By.ID, "input_8").send_keys(amazon)
        driver.find_element(By.ID, "input_30").send_keys(blurb)
        driver.find_element(By.ID, "month_9").send_keys(smonth)
        driver.find_element(By.ID, "day_9").send_keys(sday)
        driver.find_element(By.ID, "year_9").send_keys(syear)
        driver.find_element(By.ID, "month_10").send_keys(emonth)
        driver.find_element(By.ID, "day_10").send_keys(eday)
        driver.find_element(By.ID, "year_10").send_keys(eyear)
        driver.find_element(By.ID, "input_14_1004").click()
        driver.find_element(By.ID, "input_15").click()
        print("11. Successfully submitted to JotFormPro")

    def FreeKindle():
        driver.get("https://newfreekindlebooks.com/authors/")
        driver.implicitly_wait(10)
        driver.find_element(By.ID, "wdform_3_element17").send_keys(book_title)
        driver.find_element(By.ID, "wdform_10_element17").send_keys(name)
        driver.find_element(By.ID, "wdform_4_element17").send_keys(amazon)
        driver.find_element(By.ID, "wdform_2_element17").send_keys('0' + str(smonth) +'/'+ str(sday) + '/'+ str(syear))
        driver.find_element(By.ID, "wdform_7_element17").send_keys('0' + str(emonth) +'/'+ str(eday) + '/'+ str(eyear))
        driver.find_element(By.ID, "wdform_8_element17").send_keys(str(book_price))
        driver.find_element(By.ID, "wdform_5_element17").send_keys(email)
        driver.find_element(By.CSS_SELECTOR, ".button-submit").click()
        print("12. Successfully submitted to FreeKindle")
    
    def Fkbt():
        driver.get("https://fkbt.com/for-authors/free-kindle-promotion/")
        driver.implicitly_wait(10)
        driver.find_element(By.NAME, "your-name").send_keys(name)
        driver.find_element(By.NAME, "your-email").send_keys(email)
        driver.find_element(By.NAME, "PayPalEmail").send_keys(email)
        driver.find_element(By.NAME, "StateofResidence").send_keys(state_of_residence)
        driver.find_element(By.NAME, "book-link").send_keys(amazon)
        driver.find_element(By.NAME, "book-title").send_keys(book_title)
        driver.find_element(By.NAME, "book-promo-price").send_keys(str(book_price))
        driver.find_element(By.NAME, "book-genre").send_keys(book_genre)
        driver.find_element(By.NAME, "date-1").send_keys('0' + str(smonth) +'/'+ str(sday) + '/'+ str(syear) + '-' + '0' + str(emonth) +'/'+ str(eday) + '/'+ str(eyear))
        driver.find_element(By.CSS_SELECTOR, ".wpcf7-submit").click()
        print("13. Successfully submitted to Fbkt")

    def DiscountBookMan():
        driver.get("https://discountbookman.com/book-promotion/")
        driver.implicitly_wait(10)
        driver.find_element(By.ID, "input_7_1").send_keys(book_title)
        driver.find_element(By.ID, "input_7_2").send_keys(book_sypnosis)
        driver.find_element(By.ID, "input_7_3").send_keys(bio)
        driver.find_element(By.ID, "input_7_19").send_keys(amazon)
        driver.find_element(By.ID, "input_7_8").send_keys(cover_image)
        driver.find_element(By.ID, "input_7_9").send_keys(email)
        dropdown = driver.find_element(By.ID, "input_7_10")
        dropdown.find_element(By.XPATH, "//option[. = 'Fiction Books']").click()
        driver.find_element(By.ID, "input_7_11").send_keys(book_genre)
        driver.find_element(By.ID, "choice_7_13_1").click()
        driver.find_element(By.ID, "input_7_16").click()
        driver.find_element(By.ID, "input_7_16").send_keys('0' + str(smonth) +'/'+ str(sday) + '/'+ str(syear))
        driver.find_element(By.ID, "gform_submit_button_7").click()
        print("14. Successfully submitted to Discount Book Man")

    def ToplesScowboy():
        driver.get("https://toplesscowboy.com/submit-your-book/")
        driver.implicitly_wait(10)
        driver.find_element(By.ID, "input_1_1").send_keys(book_title)
        driver.find_element(By.ID, "input_1_2").send_keys(blurb)
        driver.find_element(By.ID, "input_1_3").send_keys(bio)
        driver.find_element(By.ID, "input_1_4").send_keys(cover_image)
        driver.find_element(By.ID, "input_1_5").send_keys(website)
        driver.find_element(By.ID, "input_1_6").send_keys(amazon)
        driver.find_element(By.ID, "input_1_11").send_keys(email)
        driver.find_element(By.ID, "input_1_19").click()
        dropdown = driver.find_element(By.ID, "input_1_19")
        dropdown.find_element(By.XPATH, "//option[. = 'Science Fiction']").click()
        driver.find_element(By.ID, "input_1_19").click()
        driver.find_element(By.ID, "input_1_12").send_keys(book_genre)
        driver.find_element(By.ID, "choice_1_14_1").click()
        driver.find_element(By.ID, "input_1_15").send_keys('0' + str(smonth) +'/'+ str(sday) + '/'+ str(syear))
        driver.find_element(By.ID, "gform_submit_button_1").click()
    
    BookBongo()
    EBooksHabit()
    ItsWriteNow()
    ZwoodleBooks()
    LovelyBooks()
    Freebie()
    AwesomeGang()
    PreetyHot()
    FreeBooksy()
    EReader()
    JotFormPro()
    FreeKindle()
    Fkbt()
    DiscountBookMan()
    ToplesScowboy()
    x += 1

