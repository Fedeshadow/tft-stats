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

if __name__ == '__main__':
    db_creation() #TODO implement argument parsing to run only when needed
    status = Api()
    status.champion_items_maker()

    # multithreading per region
    status.threading_region(status.player_list, status.region, "player list")
    status.threading_region(status.match_list, status.region, "match id list")
    status.threading_region(status.matches_fetch, status.region, "match analysis")

    for lang in status.languages:
        status.champion_items_maker(lang)