import sqlite3

# Initialize database
def init_db():
    conn = sqlite3.connect("image_timer.db")
    cursor = conn.cursor()
    
    # Create table for storing images
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            collection TEXT NOT NULL
        )
    ''')
    
    # Create table for storing collections
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id INTEGER,
            image_id INTEGER,
            FOREIGN KEY (collection_id) REFERENCES collections(id),
            FOREIGN KEY (image_id) REFERENCES images(id)
        )
    ''')
    
    # Create table for settings (last used configurations)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    conn.commit()
    conn.close()