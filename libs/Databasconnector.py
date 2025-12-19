import sqlite3
import os
from pathlib import Path

class DatabaseConnector:
    def __init__(self):
        # Use raw string to avoid escape sequence issues
        self.base_path = r"C:\Users\O.Feronel\OneDrive - ams OSRAM\Documents\PYTHON\QtForge Studio\db"

        # Check and create directory
        if not os.path.exists(self.base_path):
            try:
                os.makedirs(self.base_path)  # Create directory
                print(f"Created directory: {self.base_path}")
            except PermissionError as e:
                print(f"DB Error :: {str(e)}")

        # Database path
        self.db_path = os.path.join(self.base_path, "QtForge_Studio.db")
        #print(f'Database path: {self.db_path}')

    def connect(self):
        '''Connect to the SQLite database.'''
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            print(f"Critical: Error connecting to SQLite database: {e}")
            return None

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        '''Execute SQL query with optional fetching options.'''
        conn = self.connect()
        if conn is None:
            return None  # Return None if connection failed

        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = None  # For INSERT, UPDATE, DELETE queries
            conn.commit()
            return result
        except sqlite3.Error as e:
            print(f"Error executing SQL query: {e}")
            return None
        finally:
            conn.close()

    def create_tables_if_not_exist(self):
        tables = {
            "RECENT": [
                "ID INTEGER PRIMARY KEY",
                "PATH TEXT UNIQUE",
                "LAST_OPENED TEXT"
            ],
        }

        conn = self.connect()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            for table_name, columns in tables.items():
                cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
                )
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.commit()
            conn.close()



    # ##############################################################################
    # #####                            QUERY                                   #####
    # ##############################################################################

    def insert_path(self, path: str | Path, last_opened: str):
        """
        Save all valid and working paths
        """
        query = """
        INSERT OR REPLACE INTO RECENT (PATH, LAST_OPENED)
        VALUES (?, ?)
        """
        # Convert Path to str if necessary
        path_str = str(path)
        params = (path_str, last_opened)
        self.execute_query(query, params)

    def get_recent_paths(self, limit: int = 10) -> list[str]:
        """
        Fetch recent paths from the database, sorted by LAST_OPENED descending.
        Returns a list of paths as strings, up to `limit` entries.
        """
        query = f"""
        SELECT PATH 
        FROM RECENT 
        ORDER BY datetime(LAST_OPENED) DESC
        LIMIT ?
        """
        result = self.execute_query(query, (limit,), fetch_all=True)
        if result:
            # Each row is a tuple like ('C:/path/to/file',)
            return [row[0] for row in result]
        return []























    # def insert_credentials(self, host, user, port, passw):
    #     """Save Credentials to database for future use"""
    #     self.delete_credentials()
    #     query = "INSERT OR REPLACE INTO CREDENTIALS (HOST, USER, PORT, PASSWORD) VALUES (?, ?, ?, ?)"
    #     params = (host, user, port, passw)
    #     self.execute_query(query, params)


    # def delete_credentials(self):
    #     """Delete all credentials"""
    #     self.execute_query(query="DELETE FROM CREDENTIALS")


    # def get_credentials(self):
    #     """Get credentials data as a flat list (latest entry only)"""
    #     result = self.execute_query(query="SELECT * FROM CREDENTIALS ORDER BY ID DESC LIMIT 1", fetch_one=True)
    #     return list(result) if result else []



    # # ##############################################################################
    # # #####                           FOLDER QUERY                             #####
    # # ##############################################################################

    # def insert_folders(self, folder, files):
    #     """Insert folders names"""
    #     query = "INSERT INTO BINFOLDERS (FOLDER, FILES) VALUES (?, ?)"
    #     params = (folder, files,)  # Add the comma to make it a tuple
    #     self.execute_query(query, params)

    # def get_all_folders(self):
    #     """Get all folders and their file lists from the database."""
    #     result = self.execute_query(query="SELECT FOLDER, FILES FROM BINFOLDERS", fetch_all=True)
    #     return {row[0]: row[1] for row in result} if result else {}

    # def delete_folders(self):
    #     self.execute_query(query="DELETE FROM BINFOLDERS")

    # def get_folder_file(self, folder):
    #     query = "SELECT FILES FROM BINFOLDERS WHERE FOLDER = ?"
    #     params = (folder,)
    #     result = self.execute_query(query=query, params=params, fetch_all=True)
    #     return [row[0] for row in result] if result else []

    # def like_folder(self, text):
    #     """Return folder names matching the given LIKE pattern."""
    #     query = "SELECT FOLDER FROM BINFOLDERS WHERE FOLDER LIKE ?"
    #     params = (f"%{text}%",)
    #     result = self.execute_query(query=query, params=params, fetch_all=True)
    #     return [row[0] for row in result] if result else []

