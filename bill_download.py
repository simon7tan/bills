import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import urllib.request

# Load data
df = pd.read_csv('legislation_total_declutter.csv')

# Setup Selenium ChromeDriver and ChromeOptions
options = Options()
options.add_argument("--incognito")

# Specify the path to your custom Chrome binary
chrome_binary_path = os.path.join('chrome-win64/chrome.exe')
options.binary_location = chrome_binary_path

# Update the service path if needed
service = Service(os.path.join('chromedriver-win64/chromedriver.exe'))
driver = webdriver.Chrome(service=service, options=options)

# Folder for saving documents
folder_path = os.path.join('Collection')
os.makedirs(folder_path, exist_ok=True)

def search_and_download(state, bill):
    query = f"{state} {bill} filetype:pdf"
    driver.get("http://www.google.com")
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    
    # Wait for results to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h3"))
    )
    
    try:
        # Click the first search result link
        first_result = driver.find_element(By.CSS_SELECTOR, "h3").find_element(By.XPATH, "..")
        first_result.click()
        
        # Wait for the new page to load
        WebDriverWait(driver, 10).until(
            lambda driver: driver.current_url != "http://www.google.com"
        )

        # Assume the current page is the document to be downloaded
        doc_url = driver.current_url
        file_extension = doc_url.split('.')[-1]
        file_name = os.path.join(folder_path, f"{state.replace(' ', '_')}_{bill.replace(' ', '_')}.{file_extension}")
        urllib.request.urlretrieve(doc_url, file_name)
        print(f"Downloaded {file_name}")
    except Exception as e:
        print(f"Error downloading document for {query}: {e}")

# Iterate through rows in the dataframe
for index, row in df.iterrows():
    try:
        search_and_download(row['State'], row['Bill'])
    except Exception as e:
        print(f"Error processing row {index} ({row['State']}, {row['Bill']}): {e}")

driver.quit()
