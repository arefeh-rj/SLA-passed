import psycopg2

conn = psycopg2.connect(
    database="notifier_db",
    user="notifier",
    password="notifier_pw",
    host="localhost",
    port=5432
)
cur = conn.cursor()

# 1) enable extension BEFORE using CITEXT
cur.execute("CREATE EXTENSION IF NOT EXISTS citext;")

# 2) create table (matches your schema)
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  display_name TEXT NOT NULL CHECK (length(btrim(display_name)) > 0),
  email CITEXT UNIQUE,
  user_name text UNIQUE,
  phone_number TEXT,
  note TEXT,
  role TEXT CHECK (role IN ('admin','manager','member','viewer')) DEFAULT 'member',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
""")

# 3) insert rows — columns MUST match the table; use executemany for multiple rows
sql = """
INSERT INTO users (display_name, email,user_name, phone_number, note, role)
VALUES (%s, %s, %s, %s, %s, %s)
"""
rows = [
    ("arefe", "rajabian.arefeh79@gmail.com", "a.rajabian", "989334522831", "On-call", "admin"),
    ("nargess", "rajabian.arefeh99@gmail.com","n.dadkhah",  "989024610775", "",        "member"),
]
cur.executemany(sql, rows)

conn.commit()
cur.close()
conn.close()
