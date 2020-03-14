from selenium import webdriver
from selenium.webdriver.common.keys import Keys

browser = webdriver.Firefox()
browser.get('http://www.facebook.com')

myfile = open("facebookpost.txt", 'w')

email = input("Enter your email: ")
password = input("Enter your password: ")

username = browser.find_element_by_name('email')
username.clear()
username.send_keys(email)

password = browser.find_element_by_name('pass')
password.clear()
password.send_keys(password)

browser.implicitly_wait(10)
login = browser.find_element_by_xpath("//input[@value='Log In']")
login.click()

profile = browser.find_element_by_xpath("//a[@title='profile' ")
profile.click()

myfile.write("Facebook Posts of Ibraheem")


# Now at the profile page.

# This method is to scroll down the profile page.
def scroll_down():
    """A method for scrolling the page."""
    # Get scroll height.
    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to the bottom.
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load the page.
        browser.implicitly_wait(10)
        # Calculate new scroll height and compare with last scroll height.
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

scroll_down()

element = browser.find_elements_by_xpath("//div[@class='_1dwg_1w_m_q7o']/p")

for elem in element:
    myfile.write(str(element), end='\n')
