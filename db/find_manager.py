# db_users.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://notifier:notifier_pw@localhost:5432/notifier_db"
)

def get_managers_by_label(label_code: str):
    """
    Return ALL active managers for a label.
    If you want the primary manager first, it will be ordered so.
    """
    sql = """
    SELECT
        lm.is_primary,
        u.id          AS manager_id,
        u.user_name   AS manager_name,
        u.phone_number,
        l.label       AS label_code,
        l.display_name
    FROM public.ntc_labels l
    JOIN public.manager_nta lm
      ON lm.label_id = l.id
     AND lm.valid_to IS NULL           -- only active assignments
    JOIN public."users" u
      ON u.id = lm.manager_user_id
    WHERE l.label = %s
    ORDER BY lm.is_primary DESC, u.id;  -- primary manager first
    """

    with psycopg2.connect(DB_URL) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (label_code,))
            rows = cur.fetchall()
            return [dict(r) for r in rows]
