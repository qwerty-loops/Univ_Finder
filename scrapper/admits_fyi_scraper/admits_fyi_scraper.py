from bs4 import BeautifulSoup
import requests
import csv
import os
import time
#Selenium libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#from dotenv import load_dotenv
#load_dotenv()

class TableParser(object): #To parse data

    #Create initial function
    def __init__(self):
        pass
    
    #Creates a function to parse data from Admit.fyi table component
    def parse(self,table):

        #Creating an empty list to store data
        parsed_rows=[]
        #Finds the first table body
        table_body = table.find('tbody')
        #Finds all the rows with the table
        table_rows = table_body.findAll('tr')
        
        #Iterate throiugh thr rows
        for row in table_rows:
            #Finds all the td tags within a row
            table_column = row.findAll('td')
            #After cleaning and stripping td tags, they are put into a list
            columns= [col.text.strip() for col in table_column]
            #Appending rowwise into the created list
            parsed_rows.append(columns)
        print("Done with parsing data and stored as a list.")
        return parsed_rows
    
class csvWriter(object): #This is to store data in a CSV file

    def writeCSV(self,data):
        if not data:
            print("No data to write")
            return
        
        #Specifying the desired path location
        file_path = r'D:\Allen Archive\Allen Archives\NEU_academics\Semester2\Data Mining\Project\admits_fyi_scraped_data.csv'
        #Used to check whether the path exists
        file_exists=os.path.exists(file_path)

        #To release resources upon completion we use with statement for file
        with open(file_path,"a",encoding="utf-8",newline='') as f:

            #Create the CSV writer to add rows into the CSV
            writer = csv.writer(f)
            #Check if the file exists, if not just append headers
            if not file_exists:
                writer.writerow(['University', 'Status', 'Target Major', 'Term', 'GRE Verbal', 'GRE Quantitative', 'GRE Writing', 'GRE Total', 'TOEFL/IELTS', 'UG College', 'UG Major', 'GPA', 'Papers', 'Work Exp'])
            
            #If file exists add rows into CSV
            for row in data:
                writer.writerow(row)
            print("Done with storing parsed data into a CSV.")

class Scraper(object): 

    def __init__(self):
        #Returns the value of the os environment
        #self.url=os.getenv('URL')
        self.url = 'https://admits.fyi/'
        print(self.url)

    def scrape(self): #Doing selenium stuff???
        print('Starting Scraping .....')
        driver = webdriver.Chrome()
        #Gets the url
        driver.get(self.url)
        #Selenium waits max 10 seconds for the element we are searching for
        #This is the driver component
        wait = WebDriverWait(driver,10)
        #Table parser object
        tp = TableParser()
        #Tcsv Writer object
        csw = csvWriter()
        count = 0
        while True:

            #wait 5 seconds
            time.sleep(5)
            # get page_source
            html = driver.page_source
            soup = BeautifulSoup(html,"html.parser")
            #Identifying the table with admits.fyi
            table = soup.find('table',id='tbl')

            parsed_data = tp.parse(table)
            csw.writeCSV(parsed_data)
            count+=1
            print(f'Page {count}')

            try:

                next_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="tbl"]/tfoot/tr/td/ul/li[7]/a')))
                #//*[@id="tbl"]/tbody/tr[1]/td[1]/a
                #As long as next page exists, click it.
                if not next_link.get_attribute('disabled'):
                    next_link.click()
                else:
                    print('Finished traversing through all pages.')
                    break
            except TimeoutException:
                break

scraper = Scraper()
scraper.scrape()

