# setup_label_managers_m2m.py
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
            # Create the link table between labels and users (managers)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS public.manager_nta (
                    label_id        BIGINT NOT NULL REFERENCES public.ntc_labels(id) ON DELETE CASCADE,
                    manager_user_id BIGINT NOT NULL REFERENCES public."users"(id) ON DELETE RESTRICT,
                    is_primary      BOOLEAN NOT NULL DEFAULT FALSE,
                    valid_from      TIMESTAMPTZ NOT NULL DEFAULT now(),
                    valid_to        TIMESTAMPTZ,
                    PRIMARY KEY (label_id, manager_user_id)
                );
            """)
            cur.execute("""CREATE INDEX IF NOT EXISTS idx_manager_nta_manager ON public.manager_nta(manager_user_id);""")
            cur.execute("""CREATE INDEX IF NOT EXISTS idx_manager_nta_active  ON public.manager_nta(label_id) WHERE valid_to IS NULL;""")
            # Optional: enforce only one active primary manager per label
            cur.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS uq_label_primary_manager
                ON public.manager_nta(label_id)
                WHERE is_primary AND valid_to IS NULL;
            """)

            # ---- Seed links directly (no migration from manager_NTA) ----
            # Use label code + user id (manager) + is_primary
            links = [
                ("NTC-18755", 1, True),
                ("NTC-19397", 2, True),
                # add more as needed...
            ]

            # Insert by joining VALUES to labels to resolve label_id
            # (safe even if some label codes aren’t present — they’ll just not insert)
            execute_values(
                cur,
                """
                INSERT INTO public.manager_nta (label_id, manager_user_id, is_primary)
                SELECT l.id, v.manager_user_id, v.is_primary
                FROM (VALUES %s) AS v(label_code, manager_user_id, is_primary)
                JOIN public.ntc_labels l ON l.label = v.label_code
                ON CONFLICT (label_id, manager_user_id) DO NOTHING
                """,
                links,
            )

        conn.commit()
        print("✓ manager_nta table ready; seeded hard-coded links.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
