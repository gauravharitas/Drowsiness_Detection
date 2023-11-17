# Update your database schema

import sqlite3

MyDB = sqlite3.connect('Drowsy.db')
MyCursor=MyDB.cursor()

# MyCursor.execute("SELECT name FROM sqlite_master WHERE type='table';") # show tables
# tables = MyCursor.fetchall()

# for table in tables:
#     print(table[0])

# Create table
# MyCursor.execute("CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY AUTOINCREMENT, Email TEXT UNIQUE NOT NULL)")
# MyCursor.execute("CREATE TABLE IF NOT EXISTS Images_Data (id INTEGER PRIMARY KEY AUTOINCREMENT, UserId INTEGER, Photo BLOB NOT NULL, FOREIGN KEY(UserId) REFERENCES Users(id))")




# Describe table
# table_name = 'Images'
# MyCursor.execute(f"PRAGMA table_info({table_name});")
# table_info = MyCursor.fetchall()

# print("Column Info:")
# for column in table_info:
#     print(column)
