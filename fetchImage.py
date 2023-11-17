import sqlite3
MyDB = sqlite3.connect('Drowsy.db')
MyCursor = MyDB.cursor()

def get_user_id(email):
    MyCursor.execute("SELECT id FROM Users WHERE Email = ?", (email,))
    user_id = MyCursor.fetchone()
    if user_id:
        return user_id[0]
    else:
        print("User not found.")
        return None

def retrieve_all_images(email):
    user_id = get_user_id(email)

    if user_id is not None:
        SQLStatement = "SELECT * FROM Images_Data WHERE UserId = ?"
        MyCursor.execute(SQLStatement, (user_id,))
        results = MyCursor.fetchall()

        for i, result in enumerate(results):
            image_data = result[2]
            store_file_path = f"ImageOutput/{email}_img{i + 1}.jpg"

            with open(store_file_path, "wb") as file:
                file.write(image_data)
                file.close()

            print(f"Image {i + 1} retrieved into the folder Image_Output for {email}")

try:
    email = input("Enter user email to retrieve all images: ")

    retrieve_all_images(email)

except Exception as e:
    print("Sorry, an error occurred or maybe there are no images for the specified user.")
