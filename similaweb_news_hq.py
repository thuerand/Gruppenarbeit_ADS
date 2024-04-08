# similarweb_news_hq.py

# Libraries
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import random

def get_hq_from_newsagencies():
    # Read the data from the CSV file
    df = pd.read_csv('Data_cryptonews/HQ_newsagency.csv')
    
    # Filter to find rows where 'hq_location' is NaN
    domains_to_lookup = df[pd.isna(df['hq_location'])]
    
    # Only proceed if there are domains that need to be looked up
    if domains_to_lookup.empty:
        print("Every domain is already looked up.")
    else:
        print("Domains which have to get looked up:")
        print(domains_to_lookup['Domain'].to_list())

        # Configure WebDriver options
        opts = Options()
        opts.add_argument("--headless")
        ua_path = "user_agents.txt"
        ua_list = [line.rstrip('\n') for line in open(ua_path)]
        opts.add_argument("user-agent=" + random.choice(ua_list))

        # Initialize WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        
        for index, row in domains_to_lookup.iterrows():
            domain = row['Domain']
            
            try:
                # Open the SimilarWeb website with the domain
                driver.get(f"https://www.similarweb.com/website/{domain}/#overview")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/main/div/div/div[1]/section/div/div/div/div[5]/div/dl/div[4]/dd')))
                hq_element = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div/div/div[1]/section/div/div/div/div[5]/div/dl/div[4]/dd')
                hq_location = hq_element.text.strip()
                
                # Update the DataFrame if the HQ location is found
                if hq_location:
                    df.at[index, 'hq_location'] = hq_location
                else:
                    df.at[index, 'hq_location'] = np.nan

            except Exception as e:
                print(f"Failed to retrieve HQ info for {domain}: {e}")
                df.at[index, 'hq_location'] = np.nan

        # Save the updated DataFrame back to the CSV
        df.to_csv('Data_cryptonews/HQ_newsagency.csv', index=False)
        print("Updated HQ information has been saved.")

        # Close the WebDriver
        driver.quit()

get_hq_from_newsagencies()