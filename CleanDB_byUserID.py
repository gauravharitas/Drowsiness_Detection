
# import sqlite3

# MyDB = sqlite3.connect('Drowsy.db')
# MyCursor=MyDB.cursor()

# MyCursor.execute("DROP TABLE IF EXISTS Images_Data")
# print("ALL Data Deleted from the Database")
# MyDB.commit()

# except : 
#     print("Already Delete or No ")

import sqlite3

MyDB = sqlite3.connect('Drowsy.db')
MyCursor = MyDB.cursor()

user_email = input("Enter user email to retrieve all images: ")

try:
    # Delete all records for the specified user email
    MyCursor.execute("DELETE FROM Images_Data WHERE UserId = ?", (user_email,))
    MyCursor.execute("DELETE FROM Users WHERE Email = ?", (user_email,))
    MyDB.commit()
    print(f"All data for user email {user_email} deleted from the database")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    MyDB.close()
