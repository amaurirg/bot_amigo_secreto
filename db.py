import sqlite3
from methods import BotFalar
import base64


class DbBot(BotFalar):
    def __init__(self, dbname="secrets_friends.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS friends (name text, chat_id int, secret_friend text, id_friend text)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_name(self):
        stmt = "INSERT INTO friends (name, chat_id) VALUES (?, ?)"
        args = (self.first_name, self.chat_id)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_name(self, name):
        stmt = "DELETE FROM friends WHERE name = (?)"
        args = (name, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def name_friend(self, name, friend):
        friend_cod = base64.b64encode(str(friend).encode('utf-8'))
        dec_friend_cod = friend_cod.decode('utf-8')
        stmt = "UPDATE friends SET secret_friend = (?) WHERE name = (?)"
        args = (dec_friend_cod, name)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def insert_id_friend(self, id_friend, secret_friend):
        id_cod = base64.b64encode(str(id_friend).encode('utf-8'))
        dec_id_cod = id_cod.decode('utf-8')
        friend_cod = base64.b64encode(str(secret_friend).encode('utf-8'))
        dec_friend_cod = friend_cod.decode('utf-8')
        stmt = "UPDATE friends SET id_friend = (?) WHERE secret_friend = (?)"
        args = (dec_id_cod, dec_friend_cod)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_names(self):
        stmt = "SELECT name FROM friends"
        return [x[0] for x in self.conn.execute(stmt)]

    def get_friends(self):
        stmt = "SELECT name, chat_id FROM friends"
        return [[x[0], x[1]] for x in self.conn.execute(stmt)]

    def id_friend(self):
        stmt = "SELECT id_friend FROM friends WHERE chat_id = (?)"
        args = (self.chat_id,)
        return [base64.b64decode(x[0]).decode('utf-8') for x in self.conn.execute(stmt, args)]

    def id_of_name(self, id_friend):
        enc_id_friend = base64.b64encode(str(id_friend).encode('utf-8'))
        dec_id_friend = enc_id_friend.decode('utf-8')
        stmt = "SELECT chat_id FROM friends WHERE id_friend = (?)"
        args = (dec_id_friend,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def friends(self):
        stmt = "SELECT chat_id, secret_friend FROM friends"
        return [[x[0], base64.b64decode(x[1]).decode('utf-8')] for x in self.conn.execute(stmt)]
