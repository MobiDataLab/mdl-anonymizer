import sqlite3
import json
import uuid
import os
import io
from mob_data_anonymizer import CONFIG_DB_FILE


class BinaryFileManager:
    def __init__(self, database):
        self.database = database
        self.connection = None

    def connect(self):
        self.connection = sqlite3.connect(self.database)
        self.connection.row_factory = sqlite3.Row

    def close(self):
        if self.connection is not None:
            self.connection.close()

    def create_tables(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                binary BLOB NOT NULL,
                state TEXT NOT NULL,
                filename TEXT NOT NULL
            );
        """
        with self.connection:
            self.connection.execute(create_table_query)

    def insert_file(self, binary, filename):
        file_id = str(uuid.uuid4().hex)
        insert_query = """
            INSERT INTO files (id, binary, state, filename)
            VALUES (?, ?, ?, ?)
        """
        with self.connection:
            self.connection.execute(insert_query, (file_id, binary, "processing", filename))
        return file_id

    def update_file_state(self, file_id, state):
        update_query = """
            UPDATE files
            SET state = ?
            WHERE id = ?
        """
        with self.connection:
            self.connection.execute(update_query, (state, file_id))

    def get_file_state(self, file_id):
        select_query = """
            SELECT state
            FROM files
            WHERE id = ?
        """
        with self.connection:
            result = self.connection.execute(select_query, (file_id,)).fetchone()
            if result is not None:
                return result["state"]
            else:
                return None

    def get_file_binary(self, file_id):
        select_query = """
            SELECT binary, state
            FROM files
            WHERE id = ?
        """
        with self.connection:
            result = self.connection.execute(select_query, (file_id,)).fetchone()
            if result is not None and result["state"] == "processed":
                return result["binary"]
            else:
                return None

    def get_file_name(self, file_id):
        select_query = """
            SELECT filename
            FROM files
            WHERE id = ?
        """
        with self.connection:
            result = self.connection.execute(select_query, (file_id,)).fetchone()
            if result is not None:
                return result["filename"]
            else:
                return None

    def delete_file(self, file_id):
        delete_query = """
            DELETE FROM files
            WHERE id = ?
        """
        with self.connection:
            self.connection.execute(delete_query, (file_id,))

    def initialize_db(self):
        with self.connection:
            self.connection.execute('DELETE FROM files;',)

    def make_db_backup(self, filename):
        with io.open(filename, 'w') as f:
            for d in self.connection.iterdump():
                f.write('%s\n' % d)

    def restore_db_backup(self, filename):
        with open(filename, 'r') as f:
            sql = f.read()

        try:
            cursor = self.connection.cursor()
            cursor.executescript(sql)

            cursor.close()
        except sqlite3.Error as e:
            print('Error restoring backup:', e)

    def convert_to_binary(self, file_path):
        with open(file_path, 'rb') as f:
            blob = f.read()

        return blob

    def save_file(self, file, filename):
        with open(filename, 'wb') as f:
            f.write(file)
