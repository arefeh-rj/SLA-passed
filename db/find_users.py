# db_users.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Use a DSN from env or fall back to your compose values
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://notifier:notifier_pw@localhost:5432/notifier_db"
)

def get_user(user_name: str):
    
    sql = """
    SELECT id, display_name, email, user_name, phone_number, note, role,
           created_at, updated_at
    FROM users
    WHERE user_name = %s
    """
    with psycopg2.connect(DB_URL) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (user_name,))
            row = cur.fetchone()
            return dict(row) if row else None