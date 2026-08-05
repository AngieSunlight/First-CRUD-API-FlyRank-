import sqlite3

file = "tasks.db"

try:
    conn = sqlite3.connect(file)
except:
    print("DB not connected")

cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        title text NOT NULL,
        done BOOL
    );
""")

cursor.execute("SELECT COUNT(*) FROM tasks")
count = cursor.fetchone()[0]

if count == 0:
    seed = [
        ("Bake a Cake", 0),
        ("Feed the cat", 0),
        ("Finish homework",0),
    ]
    cursor.executemany(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        seed
    )
    

conn.commit()
conn.close()