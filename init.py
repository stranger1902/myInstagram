from costants import DATABASE_FILENAME

import myDatabase as DB
import utils as U
  
U.createFolders()

MyConnetionDB = DB.MyDatabase(DATABASE_FILENAME)

MyConnetionDB.connectDB()
MyConnetionDB.createTablesDB()
MyConnetionDB.closeConnection()
