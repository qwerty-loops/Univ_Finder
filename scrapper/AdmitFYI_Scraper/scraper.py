import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from parser.tableParser import TableParser
from csvWriter import CsvWriter

load_dotenv()

class Scraper(object):
    def __init__(self):
        self.url = os.getenv('URL')
    
    def scrape(self):
        driver = webdriver.Chrome()
        driver.get(self.url)
        wait = WebDriverWait(driver, 10)
        tableParser = TableParser()
        csvWriter = CsvWriter()
        
        while True:
            
            # Wait for the table to load, kept 5 seconds for now
            time.sleep(5)
            
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', id='tbl')
            
            parsed_data = tableParser.parse(table)
            csvWriter.writeCSV(parsed_data)

            try:
                next_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="tbl"]/tfoot/tr/td/ul/li[7]/a')))
                if not next_link.get_attribute('disabled'):
                    next_link.click()
                else:
                    break
            except TimeoutException:
                break