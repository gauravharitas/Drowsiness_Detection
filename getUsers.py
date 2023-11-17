import sqlite3

def get_all_users():
    MyDB = sqlite3.connect('Drowsy.db')
    MyCursor = MyDB.cursor()

    try:
        MyCursor.execute("SELECT DISTINCT Email FROM Users")
        users = MyCursor.fetchall()
        return [user[0] for user in users]
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        MyDB.close()

if __name__ == "__main__":
    all_users = get_all_users()
    
    if all_users:
        print("List of all users:")
        for user in all_users:
            print(user)
    else:
        print("No users found.")
