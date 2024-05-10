import csv
import os

class CsvMaker(object):
    def make(self, data_dict):
        if not data_dict:
            print("No data to write.")
            return

        if isinstance(data_dict, dict):
            # Convert the dictionary to a list of dictionaries
            data_list = [data_dict]
        elif isinstance(data_dict, list):
            data_list = data_dict
        else:
            print("Invalid data structure.")
            return

        keys = data_list[0].keys()
        file_path = 'gradcafe.csv'

        file_exists = os.path.exists(file_path)

        with open(file_path, 'a', encoding='utf-8', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            if not file_exists:
                dict_writer.writeheader()
            dict_writer.writerows(data_list)
