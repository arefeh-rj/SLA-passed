# db_users.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Use a DSN from env or fall back to your compose values
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://notifier:notifier_pw@localhost:5432/notifier_db"
)


def get_manager_by_label(label: str):
    sql = """
    SELECT
      m.id            AS manager_nta_id,
      m.label,
      m.display_name  AS label_display_name,
      u.id            AS manager_id,
      u.user_name          AS manager_name,
      u.email         AS manager_email
    FROM public."manager_NTA" m          -- <- quoted mixed-case
    JOIN public."users" u ON u.id = m.manager_id   -- quote if you created "users" with quotes
    WHERE m.label = %s
    LIMIT 1;
    """
    with psycopg2.connect(DB_URL) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (label,))
            row = cur.fetchone()
            return dict(row) if row else None


