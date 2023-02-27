

import mysql.connector 

host = "localhost"
user  = "root"
pswd = "12345678"
db = "Drowsiness_Detection"

MyDB = mysql.connector.connect(host = host, user = user, password = pswd, database = db)

MyCursor = MyDB.cursor()

def retrieveImage(ID):
    SQLStatement2 = "SELECT * FROM Images WHERE id = '{0}'"
    MyCursor.execute(SQLStatement2.format(str(ID)))
    MyResult = MyCursor.fetchone()[1]

    StoreFilePath = "ImageOutput/img{0}.jpg".format(str(ID))
    # print(MyResult)

    with open(StoreFilePath, "wb") as File:
        File.write(MyResult)
        File.close()

try:
    SQLStatement = "SELECT * FROM Images ORDER BY id DESC LIMIT 1"
    MyCursor.execute(SQLStatement)
    result = MyCursor.fetchall()


    lastID = int(result[0][0])

    retrieveImage(lastID)
    print("Image retrieved into the folder Image_Output")
    
except Exception as e:
    print("Sorry an error occured or May be there is no Images at the backend")
		


