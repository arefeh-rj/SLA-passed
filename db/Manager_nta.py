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
      label TEXT NOT NULL CHECK (label IN ('Technical_Operation','Data_Gateway','Risk','Tax_Evasion','Data_Management','Business_Intelligence')) DEFAULT 'Technical_Operation',
      manager_id BIGINT NOT NULL REFERENCES public."users"(id) ON UPDATE CASCADE ON DELETE RESTRICT
    );
""")

# 3) insert rows — columns MUST match the table; use executemany for multiple rows
sql = """
INSERT INTO manager_NTA (display_name, label, manager_id)
VALUES (%s, %s, %s)
"""
rows = [
    ("پروفایلینگ - عملیات فنی", "Technical_Operation", "1"),
    ("تبادل داده", "Data_Gateway","2"),
]
cur.executemany(sql, rows)

conn.commit()
cur.close()
conn.close()
