import psycopg2

from database.PostgreSQL.db_auth_data import db_name, user_name, password, host, port


class CommentsDB:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect_db(self):
        self.connection = psycopg2.connect(
            database=db_name,
            user=user_name,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.connection.cursor()

    def check_user_id_exists(self, user_id):
        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM comments WHERE user_id = %s)",
            (user_id,)
        )
        return self.cursor.fetchone()[0]

    def add_user_info(self, user_id, username):
        if not (self.check_user_id_exists(user_id=user_id)):
            self.cursor.execute(
                "INSERT INTO comments (user_id, username) VALUES (%s, %s)",
                (user_id, username)
            )
            self.connection.commit()
        else:
            return -1

    def add_comment(self, user_id, comment_text):
        self.cursor.execute(
            "UPDATE comments SET comment = %s WHERE user_id = %s",
            (comment_text, user_id)
        )
        self.connection.commit()

    def get_db_data(self):
        self.cursor.execute("SELECT * FROM comments")
        return self.cursor.fetchall()

    def clear_db(self):
        sql = "DELETE FROM comments;"
        self.cursor.execute(sql)
        self.connection.commit()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()


def upload_feedback_data(user_id, username, comment_text):
    comments_db = CommentsDB()
    comments_db.connect_db()

    # add user info (user_id, username):
    comments_db.add_user_info(
        user_id=user_id,
        username=username
    )
    # add user comment:
    comments_db.add_comment(
        user_id=user_id,
        comment_text=comment_text
    )
