# similarweb_news_hq.py

# Libraries
import os
import re
import json
import time
import random
import pandas as pd
import numpy as np  # For NaN

from bs4 import BeautifulSoup

from prettytable import from_csv

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

# Settings
import warnings
warnings.filterwarnings("ignore")

# Current working directory
print(f'Current working directory: {os.getcwd()}')

# Liste mit User-Agents für Rotation
ua_path = "user_agents.txt"
ua_list = [line.rstrip('\n') for line in open(ua_path)]
ua_list[:5]

# Set options for Chrome-Driver (regular mode)
opts = Options()
opts.add_argument("--headless")
opts.add_argument("user-agent=" + random.choice(ua_list))
service = Service(executable_path=r'C:\Tools\chromedriver\chromedriver.exe') # Set the path to the chromedriver executable
driver = webdriver.Chrome(service=service, options=opts)

def get_hq_from_newsagencies():
    # Read the data from the CSV file
    df = pd.read_csv('Data_cryptonews/HQ_newsagency.csv')
    print(df)
    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    
    for index, row in df.iterrows():
        domain = row['Domain']
        hq_location = row.get('hq_location', '')
        
        # Check if 'hq_location' is empty or NaN
        if pd.isna(hq_location):
            try:
                # Open the SimilarWeb website with the domain
                driver.get(f"https://www.similarweb.com/website/{domain}/#overview")

                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/main/div/div/div[1]/section/div/div/div/div[5]/div/dl/div[4]/dd')))
                hq_element = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div/div/div[1]/section/div/div/div/div[5]/div/dl/div[4]/dd')
                hq_location = hq_element.text.strip()
                
                # Check if the hq_location is not empty before updating
                if hq_location:
                    df.at[index, 'hq_location'] = hq_location
                else:
                    df.at[index, 'hq_location'] = np.nan  # Explicitly mark as NaN if domain doesnt exist

            except Exception as e:
                # Log the error but don't overwrite existing valid data
                print(f"Failed to retrieve HQ info for {domain}: {e}")
                # Do not overwrite cells that might already contain valid data or are marked as NaN
                if pd.isna(row['hq_location']):
                    df.at[index, 'hq_location'] = np.nan

    df.to_csv('Data_cryptonews/HQ_newsagency.csv', index=False)
    print("Updated HQ information has been saved.")

    # Close the WebDriver
    driver.quit()

get_hq_from_newsagencies()