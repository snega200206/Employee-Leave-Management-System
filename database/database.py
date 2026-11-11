
import os
import psycopg


DATABASE_URL = os.environ.get("DATABASE_URL")


def connect_db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")

    conn = psycopg.connect(
        DATABASE_URL,
        sslmode="require"
    )

    return conn


def create_tables():

    conn = connect_db()

    try:
        cursor = conn.cursor()

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

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGSERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            employee_id TEXT REFERENCES employees(employee_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_balance (
            balance_id BIGSERIAL PRIMARY KEY,
            employee_id TEXT NOT NULL REFERENCES employees(employee_id),
            leave_type TEXT NOT NULL,
            total_days INTEGER NOT NULL,
            used_days INTEGER DEFAULT 0,
            UNIQUE(employee_id, leave_type)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_applications (
            leave_id BIGSERIAL PRIMARY KEY,
            employee_id TEXT NOT NULL REFERENCES employees(employee_id),
            leave_type TEXT NOT NULL,
            from_date TEXT NOT NULL,
            to_date TEXT NOT NULL,
            total_days INTEGER NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_by TEXT,
            reviewed_at TIMESTAMP
        )
        """)

        conn.commit()
        print("PostgreSQL tables created successfully!")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    create_tables()
