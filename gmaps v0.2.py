import time
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random

def scrape():
    url = "https://www.google.com/maps"
    driver = webdriver.Chrome()
    driver.get(url)
    # WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='omnibox-singlebox']")))
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body")))
    time.sleep(random.randint(2,3))
    driver.find_element(By.XPATH, "//input[@aria-controls='ydp1wd-haAclf']").send_keys("tangkuban perahu")
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[@id='searchbox-searchbutton']").click()
    time.sleep(3)
    # WebDriverWait(driver,5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#QA0Szd")))
    driver.find_element(By.XPATH, "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]").click()
    time.sleep(3)

    rblock = []
    while len(rblock) < 200:
        
        # variabel untuk mengecek apakah scroll udah mentok
        dum = len(rblock)
        # percobaan ulang scroll takutnya scroll ga bener-bener mentok, cuma karena belum keload
        re = 0

        # scrolling
        scrollable_div = driver.find_element(By.XPATH, "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]")
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(3)
        
        # parse reviews
        response = BeautifulSoup(driver.page_source, 'html.parser')
        # rblock = response.find_all('div', class_='jJc9Ad ')
        rblock = response.css.select('div.jJc9Ad ')
        
        if dum == len(rblock):
            re += 1
            if re > 10: #dicoba 10 kali buat mastiin dia beneran mentok
                break
        else:
            re = 0 #reset nilai re kalau ternyata dia ga beneran mentok
    
    # Cari dan klik setiap tombol "more" biar teks review nya full
    more = driver.find_elements(By.CSS_SELECTOR, "button.w8nwRe.kyuRq")
    print('len(more) = '+str(len(more)))
    for i in range(len(more)):
        more[i].click()

    # Ekstrak tiap review yang ada
    hasil = BeautifulSoup(driver.page_source, 'html.parser').css.select('div.jJc9Ad ')
    rev = []
    for item in hasil:
        review = item.find('span', class_='wiI7pd').text
        rev.append(review)

    hasil = pd.DataFrame(rev, columns=['review'])
    hasil.to_excel("E:/SINATRYA/gmaps.xlsx")
    print(hasil)
    time.sleep(3)
    driver.close

scrape()