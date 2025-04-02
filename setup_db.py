import sqlite3

# Connect to the database
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Ensure users table exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        mac_address TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL
    )
''')

# Ensure attendance table exists (including GPS)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Insert Zorawar's MAC if not present
zorawar_mac = "70-BC-10-6F-1E-A7"
cursor.execute("SELECT * FROM users WHERE mac_address=?", (zorawar_mac,))
if not cursor.fetchone():
    cursor.execute("""
        INSERT INTO users (id, name, email, mac_address, role) 
        VALUES (?, ?, ?, ?, ?)
    """, (700753, "Zorawar", "zorawer@yahoo.com", zorawar_mac, "employee"))

conn.commit()
conn.close()
print("✅ Database setup complete! Zorawar's MAC Address added.")
