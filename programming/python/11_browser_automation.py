# pipenv install selenium

# install selenium driver for web browser.

from selenium import webdriver

browser = webdriver.Chrome()

# open website:
browser.get("https://github.com")

# find the link and click:
signin_link = browser.find_element_by_link_text("Sign in")
signin_link.click()

# fill out the form:
username_box = browser.find_element_by_id("login_field")
username_box.send_keys("ninjacoder22")

password_box = browser.find_element_by_id("password")
password_box.send_keys("randompw")
password_box.submit()

assert "ninjacoder22" in browser.page_source
# or:
profile_link = browser.find_element_by_class_name("user-profile-link")
link_label = profile_link.get_attribute("innerHTML")
assert "ninjacoder22" in link_label

# close browser:
browser.quit()




