import sqlite3
import csv


def db_connect():
    connect = sqlite3.connect(
        r'\app\GiGaChatTeleBot\database\feedback_db',
        check_same_thread=False
    )
    cursor = connect.cursor()

    return connect, cursor


def clear_db():
    connect, cursor = db_connect()
    cursor.execute("DELETE FROM comments")
    connect.commit()


def check_user_id_exists(user_id):
    connect, cursor = db_connect()
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM comments WHERE user_id = ?)",
        (user_id,)
    )
    result = cursor.fetchone()[0]

    return bool(result)


def db_add_user_info(user_id: int, user_name: str, user_surname: str, username: str):
    connect, cursor = db_connect()
    cursor.execute(
        'INSERT INTO comments (user_id, user_name, user_surname, username) VALUES (?, ?, ?, ?)', (user_id, user_name, user_surname, username)
    )
    connect.commit()


def db_add_comments(user_id, user_comment):
    connect, cursor = db_connect()
    cursor.execute(
        "UPDATE comments SET comment = ? WHERE user_id = ?",
        (user_comment, user_id)
    )
    connect.commit()


def db_add_mark(user_id, user_mark):
    connect, cursor = db_connect()
    cursor.execute(
        "UPDATE comments SET mark = ? WHERE user_id = ?",
        (user_mark, user_id)
    )
    connect.commit()


def get_db_data_to_array():
    connect, cursor = db_connect()
    cursor.execute('SELECT username, comment FROM comments')
    data = cursor.fetchall()
    return data

