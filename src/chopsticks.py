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

            try:
                cur.executemany('INSERT INTO user VALUES(?, ?, ?, ?)', user_tuple)

            except sqlite3.IntegrityError:
                new_tuple = tuple()
                for user in user_tuple:
                    new_tuple += ((user[1], user[0]),)

                cur.executemany('UPDATE user SET lastseen=? WHERE nickname=?', new_tuple)


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


    def userstats(self, nick):
        conn = sqlite3.connect(self.path)

        with conn:
            cur = conn.cursor()

            cur.execute('SELECT cozy,autism FROM user WHERE nickname=?', (nick,))
            stats = cur.fetchone()

        return stats


    def statsupdate(self, nick, dto):
        # checking that dto is not empty
        count = 0
        for v in dto:
            if not dto[v]:
                count += 1

        if count == len(dto):
            raise RuntimeError('empty_dto')


        conn = sqlite3.connect(self.path)
        
        with conn:
            cur = conn.cursor()
            
            cur.execute('SELECT cozy,autism FROM user WHERE nickname=?', (nick,))
            stats = cur.fetchone()

            if not dto['cozy']:
                dto['cozy'] = stats[0]
            else:
                dto['cozy'] += stats[0]

            if not dto['autism']:
                dto['autism'] = stats[1]
            else:
                dto['autism'] += stats[1]

            cur.execute('UPDATE user SET cozy=?,autism=? WHERE nickname=?', (dto['cozy'], dto['autism'], nick))

        return dto
