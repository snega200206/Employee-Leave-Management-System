
import sqlite3
import os

# Database file location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "employee_leave.db")


# Database connection
def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Create database tables
def create_tables():

    conn = connect_db()
    cursor = conn.cursor()

    # Employees Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        employee_id TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        department TEXT NOT NULL,
        designation TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        joining_date TEXT,
        is_active INTEGER DEFAULT 1
    )
    """)

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        employee_id TEXT,
        FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id)
    )
    """)

    # Leave Balance Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_balance (
        balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        leave_type TEXT NOT NULL,
        total_days INTEGER NOT NULL,
        used_days INTEGER DEFAULT 0,

        FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id),

        UNIQUE(employee_id, leave_type)
    )
    """)

    # Leave Applications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_applications (
        leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        leave_type TEXT NOT NULL,
        from_date TEXT NOT NULL,
        to_date TEXT NOT NULL,
        total_days INTEGER NOT NULL,
        reason TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
        reviewed_by TEXT,
        reviewed_at TEXT,

        FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id)
    )
    """)

    conn.commit()
    conn.close()

    print("Database created successfully!")
    print("All tables created successfully!")


# Run database creation
if __name__ == "__main__":
    create_tables()
