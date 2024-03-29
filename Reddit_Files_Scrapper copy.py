from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import StaleElementReferenceException
import numpy as np
from time import sleep
import time
import io
import datetime
import csv
import pandas as pd
import json

# import unicodecsv as csv
# from io import BytesIO
import os
import pathlib
base_dir = pathlib.Path(__file__).parent.absolute()


def createDriver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("prefs", { 
    "profile.default_content_setting_values.notifications": 2 })
    driver = webdriver.Chrome(executable_path='chromedriver', options=chrome_options)
    # driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)
    return driver

def new_process(url):
    driver = createDriver()
    driver.get(url)
    posts = scrape_new(driver)
    driver.close()
    return posts

def scrape_new(driver):
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
                sleep(5)
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
        try:
            post_data['timestamp'] = card.find_element_by_css_selector('a[data-click-id="timestamp"]').text
        except:
            print('could not find the timestamp id')
            
        try:
            post_data['comments'] = card.find_element_by_css_selector('span.FHCV02u6Cp2zYL0fhQPsO').text.split()[0]
        except:
            time.sleep(3)
            post_data['comments'] = card.find_element_by_css_selector('span.FHCV02u6Cp2zYL0fhQPsO').text.split()[0]
            # post_data['comments'] = card.find_elements_by_css_selector('span.D6SuXeSnAAagG8dKAb4O4')[1].text
            # post_data['comments'] = '0'
            # pass
        # print(type(post_data['comments']),'----------------------comments number')
        if post_data['comments'] == '0':
            return
        post_data['comments_on_post'] = get_post_comments(driver, i)
        # post_data['comments'] = len(post_data['comments_on_post'])
        return post_data
    except:
        return None

def get_post_comments(driver, i):
    try:
        url = driver.find_elements_by_css_selector('a[data-click-id="comments"]')[i].get_attribute('href')
        driver.execute_script(f"window.open('{url}');")
        driver.switch_to.window(driver.window_handles[1])
        sleep(3)
        comments_on_post = []
        try:
            # scroll_to_element(driver, driver.find_element_by_xpath("//button[contains(text(), 'View Entire Discussion')]"))
            driver.find_element_by_xpath("//button[contains(text(), 'View Entire Discussion')]").click()
        except:
            pass
        sleep(3)
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
    if 'hour ago' in timestamp or 'hours ago' in timestamp or 'days ago' in timestamp or 'week ago' in timestamp or 'weeks ago' in timestamp or 'month ago' in timestamp or 'months ago' in timestamp or 'year ago' in timestamp or 'years ago' in timestamp:
        return True
    return False

def first_project_functionality():
    urls_new = [
        # 'https://reddit.com/r/btc/new/',
        'https://reddit.com/r/bitcoin/new/',
        # 'https://reddit.com/r/ethereum/new/',
        # 'https://reddit.com/r/monero/new/',
        # 'https://reddit.com/r/dashpay/new/',
        # 'https://reddit.com/r/ethtrader/new/',
        # 'https://reddit.com/r/ethfinance/new/',
        # 'https://reddit.com/r/xmrtrader/new/',
    ]
    urls_hot = [
        # 'https://reddit.com/r/btc/hot/',
        'https://reddit.com/r/bitcoin/hot/',
        # 'https://reddit.com/r/ethereum/hot/',
        # 'https://reddit.com/r/monero/hot/',
        # 'https://reddit.com/r/dashpay/hot/',
        # 'https://reddit.com/r/ethtrader/hot/',
        # 'https://reddit.com/r/ethfinance/hot/',
        # 'https://reddit.com/r/xmrtrader/hot/',
    ]
    not_ran = True
    running = True
    counter = 1
    hour = 1
    main_csv = 'output/main.csv'
    # main_txt = 'output/main.txt'

    while running:
        if counter == 2: # here you will put 24 
            running = False
        counter += 1
        for i, _ in enumerate(urls_new):
            # result      = new_process(urls_new[i])
            # print(result,'<------ result')
            # total_vote  = hot_process(urls_hot[i])
            result = {"online_users":'1.5k',"number_of_posts": '3','data':[{'timestamp': '7 minutes ago', 'comments': '3', 'comments_on_post': ['hello how are you doing.','what is the rate for bitcoin today?', 'blahblahablah']}, {'timestamp': '7 minutes ago', 'comments': '3', 'comments_on_post': ['hello how are you doing.','what is the rate for bitcoin today?', 'blahblahablah']},{'timestamp': '7 minutes ago', 'comments': '3', 'comments_on_post': ['hello how are you doing.','what is the rate for bitcoin today?', 'blahblahablah']}]}
            total_vote = 999

            web_name = urls_hot[i].split("/")[-3]
            with open(web_name+".csv", 'a+', newline='', buffering=1,encoding='utf-8') as f:
                # print(f'total votes for {web_name} website is = {total_vote}')
                row = []
                f.write(str(hour))
                f.write('\n')
                dt = datetime.datetime.now()
                f.write(str(dt.strftime("%m/%d/%Y %H:%M")))
                f.write('\n')
                f.write(str(result['online_users']))
                f.write('\n')
                f.write(str(result['number_of_posts']))
                f.write('\n')
                f.write('"')
                # f.write('[')
                # for dictionary in result['data']:
                #     f.write(json.dumps(dictionary,ensure_ascii=True))
                # f.write(str(result['data']))
                # f.write(']')
                # f.DictWriter(str(result['data']))
                # f.write(str(result['data']))
                f.write(str(result['data']))
                f.write('"')
                f.write('\n')
                f.write(str(total_vote))
                # f.write('\n')
        files = os.listdir(base_dir)  
        files = list(filter(lambda f: f.endswith('.csv'), files))
        with open(main_csv , 'a+', newline='', buffering=1, encoding='utf-8') as f:
            text_to_write_in_main_csv_file = []
            header_text_of_all_files = []
            for _file in files:
                with open(_file, 'r',encoding='utf-8') as read_obj:
                    file_name = _file.split('.csv')[0]
                    header_text_of_all_files.append(file_name+'hour')
                    header_text_of_all_files.append(file_name+'_time_&_date')
                    header_text_of_all_files.append(file_name+'_online_users')
                    header_text_of_all_files.append(file_name+'__number_of_post')
                    header_text_of_all_files.append(file_name+'_comments')
                    header_text_of_all_files.append(file_name+'_total_votes')
                    lis = [line.split('\n') for line in read_obj]
                    for i, x in enumerate(lis):
                        # reading values from each fle
                        text_to_write_in_main_csv_file.append(x[0])
                
            # print(header_text_of_all_files)
            header_text_of_all_files = ",".join(str(x) for x in header_text_of_all_files)
            text_to_write_in_main_csv_file = ",".join(str(x) for x in text_to_write_in_main_csv_file)
            if os.stat(main_csv).st_size == 0:
                f.write(header_text_of_all_files)
                f.write('\n')
            f.write(text_to_write_in_main_csv_file)
            f.write('\n')
        for _file in files:
            os.remove(_file)
        hour += 1
        sleep(3) # how long to wait between runs
    # os.rename(main_txt , main_csv)

def hot_process(url):
    driver = createDriver()
    driver.get(url)
    total_votes = scrape_hot(driver)
    driver.close()
    return total_votes

def scrape_hot(driver):
    data = []
    screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
    i = 1
    scroll_pause_time = 2
    while True:
        # scroll one screen height each time
        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
        i += 1
        time.sleep(scroll_pause_time)
        # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
        scroll_height = driver.execute_script("return document.body.scrollHeight;")  
        # Break the loop when the height we need to scroll to is larger than the total scroll height
        # print(scroll_height,'---scroll height ---')
        # if (screen_height) * i > scroll_height:
        #     break 
        posts = driver.find_elements_by_css_selector('.Post')
        print(len(posts),'----------')
        if len(posts) > 50:
            break
    posts = driver.find_elements_by_css_selector('.Post')
    print(len(posts),'<-- posts scraped ')
    for i, post in enumerate(posts):
        try:
            vote = post.find_element_by_css_selector('div._23h0-EcaBUorIHC-JZyh6J div._1E9mcoVn4MYnuBQSVDt1gC div._1rZYMD_4xY3gRcSS3p8ODO').text
        except:
            print('this post does not seen to have a valid class name for vote.')
            # vote = post.find_element_by_css_selector('div._1E9mcoVn4MYnuBQSVDt1gC span.D6SuXeSnAAagG8dKAb4O4').text
        if vote:
            data.append(vote)
    total_votes = 0
    for value in data:
        try:
            if 'k' in value:
                value = value.replace('.', '')
                value = value.replace('k', '000')
                value = int(value)
            else:
                value = int(value)
            total_votes = total_votes + value
        except:
            print('post vote value was not convertable to int')
            # pass
    return total_votes

if __name__ == "__main__":
    first_project_functionality()
