# setup_labels_nta.py
import psycopg2
from psycopg2.extras import execute_values

DB = dict(
    database="notifier_db",
    user="notifier",
    password="notifier_pw",
    host="localhost",
    port=5432,
)

def main():
    conn = psycopg2.connect(**DB)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            # Create labels table (no migration)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS public.ntc_labels (
                    id BIGSERIAL PRIMARY KEY,
                    label TEXT NOT NULL UNIQUE,  -- e.g., 'NTC-18755'
                    display_name TEXT NOT NULL CHECK (length(btrim(display_name)) > 0)
                );
            """)

            # Seed labels directly from your hard-coded rows
            rows = [
                ("پروفایلینگ - عملیات فنی", "NTC-18755"),
                ("تبادل داده", "NTC-19397"),
                # add more as needed...
            ]
            execute_values(
                cur,
                """
                INSERT INTO public.ntc_labels (display_name, label)
                VALUES %s
                ON CONFLICT (label) DO UPDATE
                  SET display_name = EXCLUDED.display_name
                """,
                rows,
            )

        conn.commit()
        print("✓ ntc_labels table ready; seeded hard-coded rows.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
