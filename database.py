import sqlite3


db_name = "database.db"


class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def get_user_by_chat_id(self, chat_id: str) -> list:
        res = self.cursor.execute(f"""SELECT * FROM users WHERE tg_chat_id = '{chat_id}'""")
        return res.fetchone()

    def get_user_by_id(self, id: int) -> list:
        res = self.cursor.execute(f"""SELECT * FROM users WHERE id = {id}""")
        return res.fetchone()

    def create_user(self, tg_chat_id: str):
        self.cursor.execute(f"""INSERT into users (tg_chat_id, device, interface_access) VALUES ('{tg_chat_id}', 0, 1)""")
        self.conn.commit()

    def get_notifies(self) -> list:
        res = self.cursor.execute(f"""SELECT * FROM notifies""")
        return res.fetchall()

    def delete_notify_by_id(self, id: int):
        self.cursor.execute(f"""DELETE from notifies WHERE id = {id}""")
        self.conn.commit()

    def create_notify(self, chat_id: str, message: str):
        self.cursor.execute(f"""INSERT into notifies (chat_id, message) VALUES ('{chat_id}', '{message}')""")
        self.conn.commit()

    def change_user_by_id(self, tg_chat_id: str = None, id: int = None, new_chat_id: str = None, new_device: int = None):
        usr = None
        if tg_chat_id is not None:
            usr = self.get_user_by_chat_id(tg_chat_id)
        if id is not None:
            usr = self.get_user_by_id(tg_chat_id)

        ex = """UPDATE users SET """

        if new_chat_id is not None:
            ex += f"tg_chat_id = '{new_chat_id}, '"
        if new_device is not None:
            ex += f"device = {new_device}, "
        ex = ex[:-2]
        ex += f" WHERE id = {usr[0]}"

        self.cursor.execute(ex)
        self.conn.commit()

    def create_client_task(self, chat_id: str, value: str):
        self.cursor.execute(f"""INSERT into client_tasks (chat_id, value) VALUES ('{chat_id}', '{value}')""")
        self.conn.commit()

    def delete_client_task_by_id(self, id: int):
        self.cursor.execute(f"""DELETE from client_tasks WHERE id = {id}""")
        self.conn.commit()




DB = Database(db_name)
if __name__ == "__main__":
    DB.create_user("2112814290")