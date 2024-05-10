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
        file_path = r'pro_admits_fyi_scraped_data.csv'
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

    def __init__(self,url):
        #Returns the value of the os environment
        #self.url=os.getenv('URL')
        self.url = url
        #print(self.url)

    def scrape(self, unique_all_universities, unique_all_courses, last_university, last_major): #Doing selenium stuff???
        print('Starting Scraping .....')
        driver = webdriver.Chrome()
        
        # login
        
        # login_url = 'https://admits.fyi/pro'
        # driver.get(login_url)
        # time.sleep(5)
        # email = driver.find_element(By.XPATH, '//*[@id="mail"]')
        # cred_email = "allensam2012@gmail.com"
        # email.send_keys(cred_email)
        # login_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/form/ul/li[2]/button')
        # login_button.click()
        
        # time.sleep(5)
        
        main_page = "https://admits.fyi/"
        for uni in unique_all_universities:
            majors = unique_all_courses if uni != last_university else unique_all_courses[unique_all_courses.index(last_major):]
            for major in majors:
                #for dept in unique_all_departments:
                #url = main_page+'?university='+uni+'&target_major='+major+'&department='+dept\
                url = main_page+'?university='+uni+'&target_major='+major
                print(url)
        
                #Gets the url
                driver.get(url)
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
                    try:
                        #Identifying the table with admits.fyi
                        table = soup.find('table',id='tbl')

                        parsed_data = tp.parse(table)
                        csw.writeCSV(parsed_data)
                        count+=1
                        print(f'Page {count}')

                        soup_foot = soup.find('tfoot')
                        elem_list = [elem.text.strip() for elem in soup_foot]
                        page_list = elem_list[1].split('\n')[1]
                        pages = page_list.count("")
                        pages=pages+1

                        my_url = '//*[@id="tbl"]/tfoot/tr/td/ul/li[' + str(pages) + ']/a'

                        try:
                            next_link = wait.until(EC.element_to_be_clickable((By.XPATH, my_url)))
                            #As long as next page exists, click it.
                            if not next_link.get_attribute('disabled'):
                                next_link.click()
                            else:
                                print('Finished traversing through all pages.')
                                break
                        except TimeoutException:
                            break
                    except:
                        break

all_universities = []
all_courses=[]
all_departments=[]
alphabets="abcdefghijklmnopqrstuvwxyz"

#Further filters

# years=[2023,2022]
#Gre_Verbal=[130,140,150,160,170]
#Gre_Quant=[130,140,150,160,170]
print('Starting off with scraping important filter info ....')

print('Retrieving info on all Universities : ')
print('\n')
for alpha in alphabets:
    body = {'key': "University", 'value': alpha}
    r = requests.post('https://admits.fyi/typeahead', json=body)
    data = r.json()
    university_names = [item['University'] for item in data]
    all_universities.extend(university_names)

all_universities=[uni.strip().replace(' ','+') for uni in all_universities]

all_universities=[uni.strip().replace(',','%2C') for uni in all_universities]

unique_all_universities = list(dict.fromkeys(all_universities))
#print(unique_all_universities)

print('Retrieving info on all Target Majors : ')
print('\n')
for alpha in alphabets:
    body = {'key': "Target_Major", 'value': alpha}
    r = requests.post('https://admits.fyi/typeahead', json=body)
    data = r.json()
    course_names = [item['Target_Major'] for item in data]
    all_courses.extend(course_names)

all_courses=[course.strip().replace(' ','+') for course in all_courses]

unique_all_courses = list(dict.fromkeys(all_courses))
print(unique_all_courses)


# print('Retrieving info on all Undergraduate Majors : ')
# print('\n')
# for alpha in alphabets:
#     body = {'key': "Department", 'value': alpha}
#     r = requests.post('https://admits.fyi/typeahead', json=body)
#     data = r.json()
#     department_name = [item['College'] for item in data]
#     all_departments.extend(department_name)

# all_departments=[department.strip().replace(' ','+') for department in all_departments]

# unique_all_departments = list(dict.fromkeys(all_departments))
#print(unique_all_departments)

# unique_all_universities =['Arizona+State+University', 'University+of+Arizona', 'Auburn+University', 'Arkansas+State+University%2C+Jonesboro', 'Arizona+State+University%2C+Polytechnic+Campus', 'Albert+Ludwigs+University+of+Freiburg', 'Adelphi+University', 'Auckland+University+of+Technology', 'Arkansas+Tech+University', 'Alabama+A&M+University', 'University+of+California%2C+Berkeley', 'Boston+University', 'University+of+Bridgeport', 'Bradley+University', 'Brown+University', 'Bowling+Green+State+University', 'Bentley+University', 'Brock+University', 'Baruch+College+-+The+City+University+of+New+York', 'Braunschweig+University+of+Technology', 'University+of+North+Carolina%2C+Charlotte', 'Carnegie+Mellon+University', 'Purdue+University%2C+West+Lafayette', 'Illinios+Institute+of+Technology%2C+Chicago', 'University+of+Maryland%2C+College+Park', 'Clemson+University', 'University+of+Colorado%2C+Boulder', 'Columbia+University', 'Cleveland+State+University', 'California+State+University%2C+Long+Beach', 'State+University+of+New+York%2C+Buffalo', 'State+University+of+New+York%2C+Stony+Brook', 'Rutgers+University%2C+New+Brunswick', 'State+University+of+New+York%2C+Binghamton', 'Duke+University', 'State+University+of+New+York%2C+Albany', 'Drexel+University', 'Delft+University+of+Technology', 'Simon+Fraser+University', 'Dalhousie+University', 'Texas+A&M+University%2C+College+Station', 'Texas+A&M+University%2C+Kingsville', 'Texas+A&M+University%2C+Corpus+Christi', 'Texas+A&M+University%2C+Commerce', 'Eastern+Michigan+University', 'ETH+Zurich', 'Eindhoven+University+of+Technology','Embry+Riddle+Aeronautical+University', 'California+State+University%2C+Fresno', 'Florida+State+University', 'Florida+Institute+of+Technology', 'Florida+International+University%2C+Miami', 'Fairleigh+Dickinson+University', 'Fairleigh+Dickinson+University%2C+Florham', 'Fordham+University', 'Florida+Atlantic+University', 'Ferris+State+University','Georgia+Institute+of+Technology', 'George+Mason+University', 'Georgia+State+University', 'George+Washington+University', 'Gannon+University', 'Grand+Valley+State+University', 'George+Washington+University%2C+Mount+Vernon+College', 'Governors+State+University', 'George+Washington+University%2C+Virginia+Campus', 'Georgetown+University', 'Harvard+University', 'Hofstra+University', 'Hochschule+Darmstadt','Heriot-Watt+University', 'South+Dakota+School+of+Mines+and+Technology', 'University+of+Hartford', 'HEC+Paris', 'Hult+International+Business+School%2C+Boston', 'Hochschule+Bremen', 'Indiana+University%2C+Bloomington', 'Iowa+State+University', 'Indiana+University+-+Purdue+University%2C+Indianapolis', 'Illinois+State+University', 'Indiana+State+University','Imperial+College+London', 'Indiana+Tech', 'Boise+State+University', 'Johns+Hopkins+University', 'James+Cook+University%2C+Townsville', 'Jacobs+University+Bremen', 'Johnson+and+Wales+University%2C+Providence', 'New+Jersey+Institute+of+Technology', 'San+Jose+State+University', 'Rutgers%2C+The+State+University+of+New+Jersey', "Saint+Joseph's+University", 'University+of+Pittsburgh%2C+Johnstown', 'Kent+State+University', 'Kansas+State+University', 'Kettering+University%2C+Flint', 'Kennesaw+State+University', 'KTH%2C+Royal+Institute+of+Technology', 'Kaiserslautern+University+of+Technology', 'Karlsruhe+Institute+of+Technology', 'Katholieke+Universiteit%2C+Leuven', 'Kingston+University%2C+London', "King's+College+London", 'Lamar+University', 'Lehigh+University', 'Lakehead+University', 'Lawrence+Technological+University', 'Louisiana+State+University%2C+Baton+Rouge', 'Louisiana+State+University+and+A&M+College', 'Louisiana+Tech+University', 'Lewis+University', 'Long+Island+University%2C+Brooklyn', 'Michigan+Technological+University', 'University+of+Wisconsin%2C+Madison', 'Missouri+University+of+Science+and+Technology', 'Michigan+State+University', 'McGill+University', 'Massachusetts+Institute+of+Technology', 'Monash+University%2C+Melbourne', 'University+of+Wisconsin%2C+Milwaukee', 'University+of+Memphis', 'Northeastern+University', 'North+Carolina+State+University', 'New+York+University', 'University+of+New+Haven', 'Northern+Illinois+University', 'Northwest+Missouri+State+University', 'Northwestern+University', 'New+York+Institute+of+Technology%2C+Manhattan', 'New+York+Institute+of+Technology%2C+Old+Westbury', 'Oklahoma+State+University%2C+Stillwater', 'Ohio+State+University', 'Oregon+State+University', 'Ohio+State+University%2C+Columbus', 'University+of+Ottawa', 'University+of+Oklahoma', 'Old+Dominion+University', 'Oakland+University', 'Ohio+University', 'Oklahoma+City+University', 'Pennsylvania+State+University', 'Polytechnic+Institute+of+New+York+University', 'Portland+State+University', 'Pace+University', 'Polytechnic+University%2C+New+York', 'University+of+Pittsburgh', 'Penn+State+Harrisburg', 'Penn+State+Great+Valley', 'Princeton+University', "Queen's+University%2C+Kingston", 'Queen+Mary+University+of+London', 'Queensland+University+of+Technology%2C+Brisbane', 'Queens+University+of+Belfast', "Queen's+University", 'The+University+of+Queensland', 'Marquette+University', 'Macquarie+University%2C+Sydney', 'Rochester+Institute+of+Technology', 'Rensselaer+Polytechnic+Institute', 'University+of+Rochester', 'Case+Western+Reserve+University', 'Rice+University', 'RWTH+Aachen+University', 'Royal+Melbourne+Institute+of+Technology', 'Rutgers+University%2C+Newark', 'Ryerson+University', 'University+of+Southern+California', 'Stevens+Institute+of+Technology', 'Syracuse+University', 'University+of+California%2C+San+Diego', 'San+Diego+State+University', 'Santa+Clara+University', 'University+of+Washington', 'University+of+Utah', 'Texas+Tech+University', 'Texas+State+University%2C+San+Marcos', 'The+University+of+Western+Ontario', 'The+University+of+Alabama', 'University+of+Texas%2C+Dallas', 'University+of+Texas%2C+Arlington', 'University+of+Illinois%2C+Chicago', 'University+of+Florida%2C+Gainesville', 'University+of+Cincinnati', 'University+of+South+Florida', 'University+of+California%2C+Irvine', 'Virginia+Tech+University', 'Virginia+Polytechnic+Institute+and+State+University', 'University+of+Virginia', 'Vanderbilt+University', 'Villanova+University', 'Valparaiso+University', 'Virginia+Commonwealth+University', 'Virginia+State+University', 'Vrije+Universiteit+Amsterdam', 'Virginia+International+University', 'Wayne+State+University', 'Wichita+State+University', 'Wright+State+University', 'Worcester+Polytechnic+Institute', 'Western+Michigan+University', 'Washington+State+University', 'Western+Illinois+University', 'Western+University', 'University+of+Texas%2C+Austin', 'University+of+North+Texas', 'York+University%2C+Toronto', 'Yale+University', 'Youngstown+State+University', 'York+University', 'University+of+California%2C+Santa+Cruz', 'State+University+of+New+York%2C+New+Paltz', 'Northern+Arizona+University', 'California+State+University%2C+Dominguez+Hills', 'Montana+State+University+at+Bozeman']
# unique_all_courses = ['Aerospace+Engineering', 'Automotive+Engineering', 'Applied+Computer+Science', 'Applied+Computing', 'Artificial+Intelligence', 'Architecture', 'Applied+Data+Science', 'Applied+Mechanics', 'Artifical+Intelligence', 'Electrical+Engineering', 'Business+Analytics', 'Biomedical+Engineering', 'Business+Analytics+and+Information+Syste', 'Business+Analytics+Flex', 'Biotechnology', 'Business+Administration', 'Bioinformatics', 'Business+Intelligence+and+Analytics', 'Bioengineering', 'Big+Data', 'Computer+Science', 'Civil+Engineering', 'Computer+Engineering', 'Cyber+Security', 'Chemical+Engineering', 'Civil+&+Environmental+Engineering', 'Computer+&+Information+Science', 'Construction+Management', 'Chemical+and+Petroleum+Engineering', 'Computing+Science', 'Data+Science', 'Data+Analytics', 'Data+Science+and+Business+Analytics', 'Industrial+Engineering', 'Industrial+and+Systems+Engineering', 'Information+Management+and+Systems', 'Electrical+&+Computer+Engineering', 'Engineering+Management', 'Electronics+&+Communication', 'EECS', 'Environmental+Engineering', 'Engineering', 'Environmental+Mining', 'Embedded+Systems', 'Electrical+and+Electronics+Engineering', 'Finance', 'Information+Systems', 'Software+Engineering', 'Information+Technology+Management', 'Information+Technology', 'Information+Management', 'Game+Development', 'Mechanical+Engineering', 'Human+Computer+Interaction', 'Health+Informatics', 'Health+Information+Technology', 'Human+Resource+Management', 'Health+Data+Science', 'Human+Resource', 'Human+Language+Technology', 'Information+Science', 'Information+Technology+and+Analytics', 'Information+Systems+and+Operations+Manag', 'Project+Management', 'Marketing', 'Computer+Networks', 'MIS', 'Materials+Science+&+Engineering', 'Management+of+Technology', 'Management', 'Manufacturing+Engineering', 'MBA', 'Management+Science+and+Engineering', 'Machine+Learning', 'Robotics', 'Petroleum+Engineering', 'Public+Health', 'Pharmacy', 'Pharmaceutical+Science', 'Production+Engineering', 'Supply+Chain+Management', 'Structural+Engineering', 'Telecommunications+Engineering', 'Telecommunication+Engineering', 'Transportation+Engineering', 'Toxicology', 'Urban+Studies']
# unique_all_departments = ['Aeronautical+Engineering', 'Automobile+Engineering', 'Architecture', 'Aerospace+Engineering', 'Accountacy+and+Finance', 'Arts', 'Agriculture', 'Animal+Husbandry', 'Avionics', 'Advertising', 'Biotechnology', 'Biomedical+Engineering', 'Business+Administration', 'Biomedical+Informatics', 'Bioinformatics', 'Biotechnology+Engineering', 'Botany', 'Biophysics', 'Biochemical+Engineering', 'Banking+and+Insurance', 'Computer+Science', 'Civil+Engineering', 'Chemical+Engineering', 'Computer+Engineering', 'Commerce', 'Computational+Science', 'Chemistry', 'Communication+and+Computer+Engineering', 'Ceramic+Engineering', 'Control+and+Telecommunication', 'Dental', 'Electronics+and+Telecommunication', 'Production+Engineering', 'Industrial+Engineering', 'Information+Science+and+Engineering', 'Instrumentation+and+Control+Engineering', 'Information+and+Communication+Technology', 'Industrial+&+Production+Engineering', 'ECE', 'EEE', 'Electronics+Engineering', 'Electrical+Engineering', 'ENI', 'Economics', 'EECS', 'Environmental+Engineering', 'Environmental+Science+and+Engineering', 'Food+Technology', 'Information+Technology', 'Information+Science', 'Information+Systems', 'Software+Engineering', 'Mechanical+Engineering', 'Instrumentation+Engineering', 'Hotel+and+Motel+Management', 'Pharmacy', 'Mathematics', 'Other', 'Information+Management', 'Laws', 'Life+Sciences', 'Metallurgical+Engineering', 'Management+Studies', 'Mining+Engineering', 'Mechatronics+Engineering', 'Mathematics+and+Computing', 'Metallurgy+and+Material+Science', 'Manufacturing+Engineering', 'Microbiology', 'Nanotechnology', 'Nursing', 'Physics', 'Petroleum+Engineering', 'Psychology', 'Polymer+Engineering', 'Premedicine', 'Production+and+Industrial+Engineering', 'Paper+Technology', 'Physiotherapy', 'Statistics', 'Structural+Engineering', 'Telecommunication+Engineering', 'Textile+Engineering', 'Textile+Technology', 'Tool+Engineering', 'Energy+Division', 'Power+Engineering', 'Zoology']

# main_page = "https://admits.fyi/"

# Specify the last university and major where scraping stopped
last_university = "Ohio+State+University"
last_major = "Public+Health"

# Find the index of the last university and major in the lists
start_university_index = unique_all_universities.index(last_university)

# Create new lists starting from the last university and major
resume_unique_all_universities = unique_all_universities[start_university_index:]

login_url = 'https://admits.fyi/pro'
scraper = Scraper(login_url)
# scraper.scrape(unique_all_universities, unique_all_courses)

# Call the scraper with the new lists
scraper.scrape(resume_unique_all_universities, unique_all_courses, last_university, last_major)