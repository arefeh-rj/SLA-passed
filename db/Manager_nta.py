import psycopg2

conn = psycopg2.connect(
    database="notifier_db",
    user="notifier",
    password="notifier_pw",
    host="localhost",
    port=5432
)
cur = conn.cursor()

# Enable citext only if you actually plan to use the CITEXT type.
cur.execute("CREATE EXTENSION IF NOT EXISTS citext;")

# Create the table (quoted because of mixed-case name)
cur.execute("""
CREATE TABLE IF NOT EXISTS public."manager_NTA" (
    id BIGSERIAL PRIMARY KEY,
    display_name TEXT NOT NULL CHECK (length(btrim(display_name)) > 0),
    label TEXT UNIQUE,
    manager_id BIGINT NOT NULL REFERENCES public."users"(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);
""")

# Insert rows — columns must match exactly; use ints for manager_id
sql = """
INSERT INTO public."manager_NTA" (display_name, label, manager_id)
VALUES (%s, %s, %s)
ON CONFLICT (label) DO NOTHING
"""
rows = [
    ("پروفایلینگ - عملیات فنی", "NTC-18755", 1),
    ("تبادل داده", "NTC-19397", 2),
]
cur.executemany(sql, rows)

conn.commit()
cur.close()
conn.close()
