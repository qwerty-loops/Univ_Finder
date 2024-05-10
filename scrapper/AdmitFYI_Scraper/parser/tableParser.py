class TableParser(object):
    def __init__(self):
        pass

    def parse(self, table):
        
        parsed_rows = []
        
        table_body = table.find('tbody')
        table_rows = table_body.find_all('tr')
        
        for row in table_rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            parsed_rows.append(cols)
        
        return parsed_rows