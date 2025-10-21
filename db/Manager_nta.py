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
CREATE TABLE IF NOT EXISTS manager_NTA (
  id BIGSERIAL PRIMARY KEY,
  display_name TEXT NOT NULL CHECK (length(btrim(display_name)) > 0),
  label TEXT CHECK (role IN ('Technical_Operation','Data_Gateway','Risk','Tax_Evasion','Data_Management','Business_Intelligence')) DEFAULT 'Technical_Operation',
  user_name text UNIQUE,
  phone_number TEXT,
  role TEXT CHECK (role IN ('admin','manager','member','viewer')) DEFAULT 'manager',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
""")

# 3) insert rows — columns MUST match the table; use executemany for multiple rows
sql = """
INSERT INTO manager_NTA (display_name, label,user_name, phone_number, role)
VALUES (%s, %s, %s, %s, %s)
"""
rows = [
    ("پروفایلینگ - عملیات فنی", "Technical_Operation", "t.rashki", "989334522831", "manager"),
    ("تبادل داده", "Data_Gateway","a.rajabian",  "989024610775", "manager"),
]
cur.executemany(sql, rows)

conn.commit()
cur.close()
conn.close()
