import myException as EX
import costants as C
import utils as U
import sqlite3

from sqlite3 import Error
from enum import Enum

#TODO:  DEFINIRE LE FOREIGN KEY
class QUERY_DB(Enum): 
    
    # TABELLA INFORMAZIONI DI SESSIONE
    CREATE_TABLE_INFO_SESSION = '''CREATE TABLE IF NOT EXISTS INFO_SESSION
                                   (SESSION_ID text NOT NULL,
                                    PROGRESSIVO integer NOT NULL,
                                    LOGGED_USER_ID integer NOT NULL,
                                    LOGGED_USER_EMAIL text NULL,
                                    LOGGED_USER_NUMBER text NULL,
                                    COOKIES text NOT NULL,
                                    LOGIN_TIMESTAMP timestamp NOT NULL,
                                    LOGOUT_TIMESTAMP timestamp DEFAULT NULL,
                                    PRIMARY KEY(SESSION_ID, PROGRESSIVO)
                                    )'''

    # TABELLA UTENTI
    CREATE_TABLE_USERS = '''CREATE TABLE IF NOT EXISTS USER
                            (USER_ID integer NOT NULL,
                             NICKNAME text NOT NULL,
                             DT_INSERT datetime NOT NULL,
                             DT_LAST_UPDATE datetime NOT NULL,
                             PRIMARY KEY(USER_ID)
                             )'''

    # TABELLA RICHIESTE PENDING
    CREATE_TABLE_PENDING_REQUESTS = '''CREATE TABLE IF NOT EXISTS PENDING_REQUEST
                                       (SESSION_ID integer NOT NULL,
                                        PROGRESSIVO integer NOT NULL,
                                        REQUEST_ID integer NOT NULL,
                                        STATUS_CODE integer NOT NULL,
                                        TYPE_HTTP_REQUEST text NOT NULL,
                                        TYPE_REQUEST integer NOT NULL,
                                        LINK text NOT NULL,
                                        HEADER text NOT NULL,
                                        PAYLOAD text DEFAULT NULL,
                                        RESPONSE text DEFAULT NULL,
                                        RESPONSE_CODE text DEFAULT NULL, 
                                        MSG_ERROR text DEFAULT NULL,
                                        DT_INSERT datetime NOT NULL,
                                        DT_LAST_UPDATE datetime NOT NULL,
                                        PRIMARY KEY (SESSION_ID, PROGRESSIVO, REQUEST_ID)
                                        )'''

    # TABELLA DELLE PRIORITA' RICHIESTE PENDING
    CREATE_TABLE_PRIORITY_PENDING_REQUESTS = '''CREATE TABLE IF NOT EXISTS PRIORITY_PENDING_REQUEST
                                                (SESSION_ID integer NOT NULL,
                                                 PROGRESSIVO integer NOT NULL,
                                                 REQUEST_ID integer NOT NULL,
                                                 PRIORITY integer NOT NULL,
                                                 DT_INSERT datetime NOT NULL,
                                                 DT_LAST_UPDATE datetime NOT NULL,
                                                 PRIMARY KEY (SESSION_ID, PROGRESSIVO, REQUEST_ID)
                                                 )'''

    SELECT_PENDING_REQUEST = '''SELECT ID_REQUEST, TYPE_HTTP_REQUEST, TYPE_REQUEST, URL, HEADER, PAYLOAD
                                FROM PENDING_REQUEST
                                WHERE LOGGED_USER = ? 
                                        AND STATUS_CODE = 0'''
    
    SELECT_PRIORITY_PENDING_REQUEST = '''SELECT TOP 1 ID_REQUEST, TYPE_HTTP_REQUEST, TYPE_REQUEST, HEADER, PAYLOAD
                                         FROM PENDING_REQUEST a 
                                                NATURAL JOIN PRIORITY_PENDING_REQUESTS b 
                                         WHERE a.LOGGED_USER = ? 
                                                AND STATUS_CODE = 0 
                                         ORDER BY b.PRIORITY'''

    SELECT_LAST_SESSION = '''SELECT IFNULL(PROGRESSIVO, 0) + 1 AS NEW_PRG, COOKIES, LOGOUT_TIMESTAMP 
                             FROM INFO_SESSION a
                             WHERE a.SESSION_ID = ? 
                                    AND a.LOGGED_USER_ID = ?
                                    AND PROGRESSIVO = (SELECT IFNULL(MAX(PROGRESSIVO), 0) FROM INFO_SESSION b WHERE b.SESSION_ID = ? AND b.LOGGED_USER_ID = ?)'''

    SELECT_LAST_AVAILABLE_SESSION = '''SELECT IFNULL(PROGRESSIVO, 0) + 1 AS NEW_PRG, COOKIES 
                                       FROM INFO_SESSION a
                                                JOIN USER b ON a.LOGGED_USER_ID = b.USER_ID
                                       WHERE (b.NICKNAME = ? OR a.LOGGED_USER_EMAIL = ? OR a.LOGGED_USER_NUMBER = ?)
                                                AND a.LOGOUT_TIMESTAMP IS NULL
                                                AND PROGRESSIVO = (SELECT IFNULL(MAX(PROGRESSIVO), 0) FROM INFO_SESSION c WHERE c.LOGGED_USER_ID = b.USER_ID AND a.SESSION_ID = c.SESSION_ID AND c.LOGOUT_TIMESTAMP IS NULL)'''

    INSERT_INFO_SESSION = '''INSERT INTO INFO_SESSION VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''

    UPDATE_ALL_LOGOUT_SESSION = '''UPDATE INFO_SESSION 
                                   SET LOGOUT_TIMESTAMP = ? 
                                   WHERE (LOGGED_USER_ID = ?
                                            OR
                                          LOGGED_USER_ID = (SELECT USER_ID FROM USER WHERE NICKNAME = ?)
                                            OR
                                          LOGGED_USER_EMAIL = ?
                                            OR
                                          LOGGED_USER_NUMBER = ?
                                          )
                                   AND LOGOUT_TIMESTAMP IS NULL'''
    
    UPDATE_LOGOUT_SESSION = '''UPDATE INFO_SESSION SET LOGOUT_TIMESTAMP = ? WHERE SESSION_ID = ?'''

    SELECT_USER = '''SELECT USER_ID FROM USER WHERE USER_ID = ? '''
    
    INSERT_USER = '''INSERT INTO USER VALUES (?, ?, ?, ?)'''

    UPDATE_USER = '''UPDATE USER SET DT_LAST_UPDATE = ? WHERE USER_ID = ? '''

class MyDatabase():

    def __init__(self, nameDB): self.databaseName = nameDB

    def connectDB(self, set_trace_callback=False):

        try:

            self.MyConnection = sqlite3.connect(self.databaseName)

            self.MyConnection.row_factory = sqlite3.Row

            if set_trace_callback: self.MyConnection.set_trace_callback(print)

            U.ScriviLog(f"Connected to the database '{self.databaseName}'", U.LEVEL.INFO)

        except Error as err: raise EX.MyDatabaseException(err)

    def createTablesDB(self):

        self.executeQuery(QUERY_DB.CREATE_TABLE_PRIORITY_PENDING_REQUESTS, isTransation=True)
        self.executeQuery(QUERY_DB.CREATE_TABLE_PENDING_REQUESTS, isTransation=True)
        self.executeQuery(QUERY_DB.CREATE_TABLE_INFO_SESSION, isTransation=True)
        self.executeQuery(QUERY_DB.CREATE_TABLE_USERS, isTransation=True)

        U.ScriviLog(f"Tables within database '{self.databaseName}' are created SUCCESSFULLY", U.LEVEL.INFO)

    def executeQuery(self, query, parameters=(), isTransation=False):

        if not isinstance(isTransation, bool): raise EX.MyTypeException(f"The parameter 'isTransation' is NOT a Boolean --> {type(query)}")

        Result = self.MyConnection.cursor().execute(query.value, parameters)

        if isTransation: self.MyConnection.commit()

        return Result

    def closeConnection(self): 
        
        try: self.MyConnection.close()
        
        except Exception as err: raise EX.MyDatabaseException(err)

        U.ScriviLog(f"Connetion to the database '{self.databaseName}' is closed SUCCESSFULLY", U.LEVEL.INFO)
