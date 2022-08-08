import sqlite3

connection = sqlite3.connect("database.db")


cursor = connection.cursor()
with open('queries/create_tables.sql') as f:
    query = f.read()
cursor.executescript(query)
connection.close()