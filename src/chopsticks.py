import os, sqlite3

class Chopsticks:
    def __init__(self, path):
        self.path = path


    def setup(self, table_structure):
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        
        for table in table_structure:
           cur.execute(table) 

        conn.commit()
        cur.close()
        conn.close()

