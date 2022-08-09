from multiprocessing import current_process
import sqlite3
from config import *
from classes import * 
import os


def db_creation():
    if os.path.exists(db):
        os.remove(db)
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    with open('queries/create_tables.sql') as f:
        query = f.read()
    cursor.executescript(query)
    
    connection.close()
    print('database setup done')


db_creation()
status = Api()

status.player_list()


connection = sqlite3.connect(db)
cursor = connection.cursor()

for p in cursor.execute('select * from player'):
    print(p)
cursor.close()