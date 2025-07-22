import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

sample_users = [
    ('John Doe', 'john@example.com', 'password123'),
    ('Jane Smith', 'jane@example.com', 'secret456'),
    ('Bob Johnson', 'bob@example.com', 'qwerty789')
]

for name, email, plain_pw in sample_users:
    hashed_pw = generate_password_hash(plain_pw)
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_pw))

conn.commit()
conn.close()
print("✅ Database initialized with secure sample users")
