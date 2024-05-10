import csv 
import os

class CsvWriter(object):
    def writeCSV(self, data):
        if not data:
            print('No data to write')   
            return
        
        file_path = r'Scraped_Dataset\scraped_data.csv'
        file_exits = os.path.exists(file_path)
        
        with open(file_path, 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            
            if not file_exits:
                writer.writerow(['University', 'Status', 'Target Major', 'Term', 'GRE Verbal', 'GRE Quantitative', 'GRE Writing', 'GRE Total', 'TOEFL/IELTS', 'UG College', 'UG Major', 'GPA', 'Papers', 'Work Exp'])
                
            for row in data:
                writer.writerow(row)