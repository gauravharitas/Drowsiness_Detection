
import sqlite3

MyDB = sqlite3.connect('Drowsy.db')
MyCursor=MyDB.cursor()

MyCursor.execute("DROP TABLE IF EXISTS IMAGES")
print("ALL Data Deleted from the Database")
MyDB.commit()

# except : 
#     print("Already Delete or No ")