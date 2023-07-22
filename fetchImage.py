
import sqlite3
MyDB = sqlite3.connect('Drowsy.db')
MyCursor=MyDB.cursor()

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
    SQLStatement = "SELECT * FROM Images ORDER BY id ASC" #LIMIT 1
    MyCursor.execute(SQLStatement)
    result = MyCursor.fetchall()

    SQLStatement = "select count(*) from Images;" #LIMIT 1
    MyCursor.execute(SQLStatement)
    rows = MyCursor.fetchone() # <<<---- it is returning tuple
    # print(type(rows[0])) <<<--- its integer
    # print(rows)
    for i in range(0, rows[0]):
        lastID = int(result[i][0])

        retrieveImage(lastID)
        print(f"Image {i+1} retrieved into the folder Image_Output")
    

    # print(result[0][1])
    # lastID = int(result[0][0])

    # retrieveImage(lastID)
    # print("Image retrieved into the folder Image_Output")
    
except Exception as e:
    print("Sorry an error occured or May be there are no Images at the Backend.")
		


