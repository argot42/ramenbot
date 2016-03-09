import sys, sqlite3

class Chopsticks:
    def __init__(self, path):
        self.path = path


    def setup(self, table_structure):
        try:
            conn = sqlite3.connect(self.path)
            cur = conn.cursor()
            
            cur.executescript(table_structure)

            conn.commit()

        except sqlite3.Error as e:
            if conn:
                conn.rollback()

            print("Error %s" % e.args[0])
            sys.exit(1)

        finally:
            if conn:
                conn.close()

    def userub(self, user_tuple):
        conn = sqlite3.connect(self.path)

        with conn:
            cur = conn.cursor()
            cur.executemany('INSERT OR REPLACE INTO user VALUES(?, ?)', user_tuple)


    def user_rts(self, nickname):
        conn = sqlite3.connect(self.path)

        with conn:
            cur = conn.cursor()
            cur.execute('SELECT lastseen FROM user WHERE nickname=?', (nickname,))
            
            data = cur.fetchone()

        if data:
            data = data[0]

        return data


    def storemsg(self, sender, receiver, body, ispriv):
       conn = sqlite3.connect(self.path)

       with conn:
           cur = conn.cursor()

           complete_msg = str()
           for word in body:
               complete_msg += word + ' '

           cur.execute('INSERT INTO msg(body, sender_id, receiver_id, priv) VALUES(?, ?, ?, ?)', (complete_msg, sender, receiver, ispriv))
           

    def retrievemsg(self, receiver):
        conn = sqlite3.connect(self.path)

        with conn:
            cur = conn.cursor()

            cur.execute('SELECT sender_id,body,priv FROM msg WHERE receiver_id=?', (receiver,))
            msgs = cur.fetchall() 

            cur.execute('DELETE FROM msg WHERE receiver_id=?', (receiver,))

        return msgs
