import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]

def init_db():
    try:
        conn = psycopg.connect(DATABASE_URL)
    except Exception as e:
        print("DB not connected:", e)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        seed = [
            ("Bake a Cake", False),
            ("Feed the cat", False),
            ("Finish homework", False),
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (%s, %s)",
            seed
        )

    conn.commit()
    conn.close()


def get_every_task():
    try:
        conn = psycopg.connect(DATABASE_URL)
    except Exception as e:
        print("DB not connected:", e)
    cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
    cursor.execute("SELECT * FROM tasks ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return rows

def specify_task(id):
    try:
        conn = psycopg.connect(DATABASE_URL)
    except Exception as e:
        print("DB not connected:", e)
    # row_factory=psycopg.rows.dict_row, tells psycopg to shape each row as a dictionary
    cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (id,))
    row = cursor.fetchone()
    conn.close()
    return row

def addition(task_data):
    try:
        conn = psycopg.connect(DATABASE_URL)
    except Exception as e:
        print("DB not connected:", e)
    cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
    cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *", (task_data.title,False,))
    conn.commit()
    new_task = cursor.fetchone()
    conn.close()
    return new_task

def replace(id, task_data):
    try:
        conn = psycopg.connect(DATABASE_URL)
    except Exception as e:
        print("DB not connected:", e)
    cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
    cursor.execute("UPDATE tasks SET title = %s, done = %s WHERE id = %s", (task_data.title, task_data.done, id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        return None
    conn.close()
    return {"id": id, "title": task_data.title.strip(), "done": task_data.done}

def delete(id):
    try:
        conn = psycopg.connect(DATABASE_URL)
    except Exception as e:
        print("DB not connected:", e)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (id,))
    if cursor.rowcount == 0:
        conn.close()
        return None
    conn.commit()
    conn.close()
    return True
    

if __name__ == "__main__":
    init_db()