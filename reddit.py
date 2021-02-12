from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import StaleElementReferenceException
import numpy as np
from time import sleep

def process(url):
    chrome_options = Options()
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("prefs", { 
    "profile.default_content_setting_values.notifications": 2 })
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    posts = scrape(driver)
    driver.close()
    return posts

def scrape(driver):
    scrolling = True
    posts = dict()
    data = []
    consecutive_post_count_older_than_one_hour = 0
    is_consecutive = True
    try:
        online_users = driver.find_elements_by_xpath('//div[@class="_3XFx6CfPlg-4Usgxm0gK8R"]')[1].text
    except:
        online_users = 0
    while scrolling:
        sleep(5)
        page_cards = driver.find_elements_by_css_selector('.Post')
        for i, card in enumerate(page_cards):
            if i+1 < len(page_cards):
                post = get_post_data(driver, card, i)
                scroll_to_element(driver, page_cards[i+1]) #scrolling to next post
                sleep(2)
            if post and not more_than_hour_ago(post['timestamp']):
                is_consecutive = False
                consecutive_post_count_older_than_one_hour = 0
                data.append(post)
            elif is_consecutive: 
                consecutive_post_count_older_than_one_hour +=1
            is_consecutive = True
            if consecutive_post_count_older_than_one_hour >= 3:
                scrolling = False
                break
    posts['online_users'] = online_users
    posts['number_of_posts'] = len(data)
    posts['data'] = data
    return posts

def scroll_to_element(driver, element):
    """Mimics human scrolling behavior and will put the element with 70 pixels of the center of the current viewbox."""
    window_height = driver.execute_script("return window.innerHeight")
    start_dom_top = driver.execute_script("return document.documentElement.scrollTop")
    element_location = element.location['y']
    desired_dom_top = element_location - window_height/2 #Center It!
    to_go = desired_dom_top - start_dom_top
    cur_dom_top = start_dom_top
    while np.abs(cur_dom_top - desired_dom_top) > 70:
        scroll = np.random.uniform(2,69) * np.sign(to_go)
        driver.execute_script("window.scrollBy(0, {})".format(scroll))
        cur_dom_top = driver.execute_script("return document.documentElement.scrollTop")
        sleep(np.abs(np.random.normal(0.0472, 0.003)))

def get_post_data(driver, card, i):
    try:
        post_data = dict()
        post_data['timestamp'] = card.find_element_by_css_selector('a[data-click-id="timestamp"]').text
        try:
            post_data['comments'] = card.find_elements_by_css_selector('span.D6SuXeSnAAagG8dKAb4O4')[1].text
        except:
            post_data['comments'] = card.find_element_by_css_selector('span.FHCV02u6Cp2zYL0fhQPsO').text.split()[0]
        post_data['comments_on_post'] = get_post_comments(driver, post_data['comments'], i)
        return post_data
    except:
        return None

def get_post_comments(driver, comments, i):
    try:
        url = driver.find_elements_by_css_selector('a[data-click-id="comments"]')[i].get_attribute('href')
        driver.execute_script(f"window.open('{url}');")
        driver.switch_to.window(driver.window_handles[1])
        sleep(2)
        comments_on_post = []
        try:
            scroll_to_element(driver, driver.find_element_by_xpath("//button[contains(text(), 'View Entire Discussion')]"))
            driver.find_element_by_xpath("//button[contains(text(), 'View Entire Discussion')]").click()
        except:
            pass
        sleep(2)
        for comment in driver.find_elements_by_css_selector('.P8SGAKMtRxNwlmLz1zdJu.Comment'):
            try:
                comments_on_post.append(comment.find_element_by_css_selector('._3tw__eCCe7j-epNCKGXUKk ._3cjCphgls6DH-irkVaA0GM ._292iotee39Lmt0MkQZ2hPV.RichTextJSON-root ._1qeIAgB0cPwnLhDF9XSiJM').text)
            except:
                pass
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return comments_on_post
    except:
        return None

def more_than_hour_ago(timestamp):
    if 'hour ago' in timestamp or 'hours ago' in timestamp or 'day ago' in timestamp or 'days ago' in timestamp or 'week ago' in timestamp or 'weeks ago' in timestamp or 'month ago' in timestamp or 'months ago' in timestamp or 'year ago' in timestamp or 'years ago' in timestamp:
        return True
    return False

if __name__ == "__main__":
    try:
        urls = [
            'https://reddit.com/r/btc/new/',
            'https://reddit.com/r/bitcoin/new/',
            # 'https://reddit.com/r/ethereum/new/',
            # 'https://reddit.com/r/monero/new/',
            # 'https://reddit.com/r/dashpay/new/',
            # 'https://reddit.com/r/ethtrader/new/',
            # 'https://reddit.com/r/ethfinance/new/',
            # 'https://reddit.com/r/xmrtrader/new/',
        ]
        results = []
        for i, url in enumerate(urls):
            results.append(process(url))
        for i, result in enumerate(results):
            print(f'Next printed result is of this url : {urls[i]}')
            print(result)
    except:
        pass