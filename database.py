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

if __name__ == "__main__":
    init_db()