from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import csv
import re

def get_scale_text():
    # Find the scale element
    scale_element = driver.find_element(By.ID, "U5ELMd").text
    return scale_element

def adjust_zoom(current_scale):
    # Function to adjust google maps's scale
    current_scale = current_scale

    # Strip the scale maps (Usually, google maps include the distance units. i.e. 500 m, 2 km)
    if 'km' in current_scale:
        current_scale_value = float(current_scale.replace(' km', '').strip())
    elif 'm' in current_scale:
        current_scale_value = float(current_scale.replace(' m', '').strip()) / 1000 #Convert meters to km
    else:
        raise Exception("Unknown scale format")

    zoom_in_button = driver.find_element(By.ID, "widget-zoom-in")
    zoom_out_button = driver.find_element(By.ID, "widget-zoom-out")

    # While current scale isn't close to the target (1 km), zoom in/out
    while abs(current_scale_value - 1) > 0.1:
        if current_scale_value > 1:
            # Zoom in (Scroll up)
            action.click(zoom_in_button).perform()
        else:
            # Zoom out (scroll down)
            action.click(zoom_out_button).perform()
        
        time.sleep(1)
        current_scale = get_scale_text()

        if 'km' in current_scale:
            current_scale_value = float(current_scale.replace(' km', '').strip())
        elif 'm' in current_scale:
            current_scale_value = float(current_scale.replace(' m', '').strip()) / 1000
        else:
            raise Exception('Unknown scale format')

start_time = time.time()

kecamatans = ["Selo", "Ampel", "Gladagsari", "Cepogo", "Musuk", "Tamansari", "Boyolali", "Mojosongo", "Teras", "Sawit", "Banyudono", "Sambi", "Ngemplak", "Nogosari", "Simo", "Karanggede", "Klego", "Andong", "Kemusu", "Wonosegoro", "Wonosamodro", "Juwangi"]
keyword = "Warung Makan"

for kecamatan in kecamatans:
    # 0. Set up the Chrome WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=chrome_options)
    action = ActionChains(driver)

    # 1. Navigate to Google Maps
    driver.get("https://www.google.com/maps")

    # 2. Perform a Location search
    search_box = driver.find_element(By.ID, "searchboxinput")

    # Search for the government office first
    search_box.send_keys(f"Kantor Kecamatan {kecamatan} Boyolali")
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

    # Search the keyword
    search_box.clear()
    search_box.send_keys(f"{keyword} di {kecamatan} Boyolali")
    search_box.send_keys(Keys.RETURN)
    print("Began searching")
    
    # Scale the google maps display
    time.sleep(2)
    adjust_zoom(get_scale_text())
    print("Success adjusting the scale")        

    # 3. Extract Results Dynamically
    # Wait for result to load
    time.sleep(2)

    # Scroll through the list of results
    results = []
    i = 1

    while True:
        # Find all result elements
        locations = driver.find_elements(By.CLASS_NAME, "hfpxzc")
        time.sleep(1)

        # Scroll to the last element found on the results
        action.move_to_element(locations[-1]).perform()
        time.sleep(1)
        locations[-1].send_keys(Keys.PAGE_DOWN)

        try:
            eol = driver.find_element(By.CLASS_NAME, "HlvSq")
            if eol.is_displayed:
                for location in locations:
                    try:
                        name = location.get_attribute("aria-label")
                        link = location.get_attribute("href")
                        results.append({
                            "name": name,
                            "kecamatan" : kecamatan,
                            "link": link
                        })
                    except Exception as e:
                        print(f"Error: {e}")
                break
        except:
            pass
        print(f"Loop: {keyword}_{kecamatan} - {i} done")
        i = i+1
    print(f"Loop keyword: {keyword}_{kecamatan} done")

    # 4. Save the data to CSV
    with open(f'Result\\{keyword}_{kecamatan}.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'link', 'kecamatan'])
        writer.writeheader()
        for result in results:
            writer.writerow(result)

    print(f"Keyword: {keyword}_{kecamatan} has been done in: {time.time()-start_time:.2f} seconds")

time.sleep(2)
driver.quit()

print(f"Program has been sucesfully executed: {time.time()-start_time:.2f} ")