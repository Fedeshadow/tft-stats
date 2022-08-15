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


#db_creation()
status = Api()

# multithreading per region
#status.threading_region(status.player_list, status.region, "player list")

status.match_list()

connection = sqlite3.connect(db)
cursor = connection.cursor()

for m in cursor.execute('select * from matches'):
    print(m)
cursor.close()